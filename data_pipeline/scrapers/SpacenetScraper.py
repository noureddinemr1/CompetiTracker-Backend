from datetime import*
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re

# Load environment variables
load_dotenv()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://noureddinemarzougui19:Fakeprofile123*@cluster0.tx9muur.mongodb.net/")
DB_NAME = "CompetiTracker"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def save_to_db(collection_name, data):
    """ Save data to MongoDB """
    collection = db[collection_name]
    if isinstance(data, list) and data:
        collection.insert_many(data)
    elif data:
        collection.insert_one(data)

def update_db(collection_name, query, data):
    """ Update existing records in MongoDB """
    collection = db[collection_name]
    collection.update_many(query, {"$set": data})

def get_from_db(collection_name, query):
    """ Retrieve data from MongoDB """
    collection = db[collection_name]
    return collection.find_one(query)

class SpacenetScraper:
    def __init__(self):
        self.url = "https://spacenet.tn/"
        competitor = get_from_db("competitors", {"url": self.url})

        if not competitor:
            data ={
                "name": "SpaceNet",
                "url": self.url,
                "logo": "https://spacenet.tn/img/logo-mobile.svg",
            }
            save_to_db("competitors",data)
            competitor = get_from_db("competitors", {"url": self.url})

        self.competitor_id = competitor["_id"]
        self.chrome_driver_path = r"C:\Users\marzo\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        # Automatically detect and install the latest compatible ChromeDriver
        self.driver = webdriver.Chrome(
            service = Service(self.chrome_driver_path),
            options=self.chrome_options
        )

    def get_urls(self):
        if not self.competitor_id:
            print("Competitor ID is missing. Skipping scraping.")
            return
        
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(2)

            links = set()

            for i in [1, 2]:
                li_xpath = f'//*[@id="sp-vermegamenu"]/ul/li[{i}]'
                li_element = self.driver.find_element(By.XPATH, li_xpath)
                soup = BeautifulSoup(li_element.get_attribute('outerHTML'), 'html.parser')

                for sub_li in soup.find_all('li', class_="item-3"):
                     a_tag = sub_li.find('a', href=True)
                     if a_tag:
                        href = a_tag['href']
                        if href != "javaScript:void(0);":
                            links.add(href)

            sorted_links = sorted(links)
            if not sorted_links:
                print("No product URLs found.")
                return

            data_entry = {
                "competitor": self.competitor_id,
                "scrapedAt": datetime.now(UTC),
                "urls": sorted_links,
            }

            doc = get_from_db("urls", {"competitor": self.competitor_id})
            if doc:
                update_db("urls", {"competitor": self.competitor_id}, data_entry)
            else:
                save_to_db("urls", data_entry)
            
            print("Scraping completed successfully.")

        except Exception as e:
            print(f"Error occurred during scraping: {e}")

        finally:
            self.driver.quit()



    def get_category(self, url):
        """Extract category from URL and replace dashes with spaces"""
        category = re.sub(r'^\d+-', '', url)
        return category.replace("-", " ")


    def scrape_page(self, page_url,category):
        """Scrape product details from a single category page"""
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch page: {page_url} ({e})")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        products = []

        product_list = soup.find('div', id='box-product-grid')
        if not product_list:
            print(f"No products found on page: {page_url}")
            return []
        
        for item in product_list.find_all('div', class_='field-product-item'):
            product_name_elem = item.find('h2', class_='product_name')
            price_elem = item.find('span', class_='price')
            link_elem = item.find('a', class_='product-thumbnail')
            stock_status_elem = item.find('div', class_='product-quantities')
            ref_elem = item.find('div', class_='product-reference')
            discount_elem = item.find('span', class_='discount-amount')
            image_elem = item.find('img', class_='img-responsive product_image')

            # Skip if price is missing or invalid
            if not price_elem or not price_elem.text.strip():
                continue

            product_price = price_elem.text.strip()
            match = re.search(r'\d+', product_price)
            if not match:
                continue

            price = float(match.group())
            livraison = "Gratuite" if price >= 300 else "Payante"

            products.append({
                'competitor': self.competitor_id,
                'ref': ref_elem.text.strip().replace("[", "").replace("]", "") if ref_elem else "N/A",
                'url': link_elem.get("href") if link_elem else "No URL",
                'product_name': product_name_elem.text.strip() if product_name_elem else "Unknown",
                'product_price': product_price,
                'discount': discount_elem.text.strip() if discount_elem else "No Discount",
                'category': category,
                'stock_status': stock_status_elem.text.strip() if stock_status_elem else "Epuisé",
                'description': "",
                'livraison': livraison,
                'image': image_elem.get("src") if image_elem else "No Image",
                'LastUpdate': datetime.now(UTC)
            })
        return products

    def scrape_element(self, base_url):
        """Scrape all pages for a single category"""
        page_num = 1
        all_products = []
        category = self.get_category(base_url)

        while True:
            url = f"{base_url}?page={page_num}"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')

            # Check for the "next" button
            next_button = soup.find('a', class_='next js-search-link')
            
            products_on_page = self.scrape_page(url, category)
            if not products_on_page:
                break

            all_products.extend(products_on_page)

            if not next_button:
                break

            page_num += 1

        return all_products
    def get_product_id(self,url):
        product = get_from_db("products",{"url" : url})
        return product["_id"]
    def scrape_all(self):
        """Main function to scrape all categories"""
        #self.get_urls()
        mytek = get_from_db("urls", {"competitor": self.competitor_id})

        if not mytek or "urls" not in mytek:
            print("No URLs found in database.")
            return

        for url in mytek["urls"]:
            print(f"Scraping: {url}")
            returned = self.scrape_element("https://spacenet.tn"+url)
            if returned:
                save_to_db("products", returned)
                print("products saved to db")
                history = []
                for p in returned : 
                    elem = {
                        'product' : self.get_product_id(p["url"]),
                        'competitor' : p['competitor'],
                        'price' : p["product_price"],
                        'stock_status' : p["stock_status"],
                        'scrapedAt' : p["LastUpdate"]
                    }
                    history.append(elem)
                save_to_db("product_history",history)
                print(f"Scraped {len(returned)} products from {url}")
            else:
                print(f"Skipping {url} due to scraping error.")

if __name__ == "__main__":
    scraper = SpacenetScraper()
    scraper.scrape_all()
