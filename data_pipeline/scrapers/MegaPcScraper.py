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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

class MegaPcScraper:
    def __init__(self):
        self.url = "https://megapc.tn/"
        competitor = get_from_db("competitors", {"url": self.url})
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        

        if not competitor:
            data ={
                "name": "MegaPc",
                "url": self.url,
                "logo": "https://megapc.tn/_next/image?url=%2Fassets%2Fimages%2Fmega.png&w=256&q=75",
            }
            save_to_db("competitors",data)
            competitor = get_from_db("competitors", {"url": self.url})

        self.competitor_id = competitor["_id"]


    def get_urls(self):
        self.chrome_driver_path = r"C:\Users\marzo\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(self.chrome_driver_path),
            options=self.chrome_options
        )

        if not self.competitor_id:
            print("Competitor ID is missing. Skipping scraping.")
            return

        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 10)  

            # 1. Click the main menu button
            menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="siteHeader"]/div/div[3]/div/div/div[1]/button')))
            menu_button.click()

            # 2. Wait for the <li> elements to load
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul > li.transition-colors')))

            # 3. Get the first 5 <li> elements
            li_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul > li.transition-colors')[:5]

            links = set()

            for index, li_element in enumerate(li_elements):
                try:
                    # Scroll to the element to ensure it's in view (important for headless mode)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", li_element)

                    # Click on the <li> to reveal its <a> children
                    li_element.click()

                    # Wait for the inner <a> tags to load
                    time.sleep(1.5)  # or use WebDriverWait if there's a consistent pattern

                    # Re-fetch the updated DOM
                    soup = BeautifulSoup(self.driver.page_source, "html.parser")

                    # Look inside the specific <li> again
                    refreshed_li = soup.select('ul > li.transition-colors')[index]

                    for a_tag in refreshed_li.find_all("a", href=True):
                        href = a_tag['href']
                        if href != "javascript:void(0);":
                            links.add(href)

                except Exception as inner_e:
                    print(f"Error with li {index+1}: {inner_e}")
                    continue

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
            product_name = item.find('h2', class_='product_name')
            product_price = item.find('span', class_='price').text.strip()
            #remove the letters with re
            match = re.search(r'\d+', product_price)
            price = float(match.group())
            link = item.find('a', class_="product-thumbnail")
            stock_status = item.find('div', class_='product-quantities')
            ref = item.find('div', class_='product-reference')
            discount = item.find('span', class_='discount-amount')
            image = item.find('img', class_="img-responsive product_image")
            if price>=300 : 
                livraison = "Gratuite"
            else:
                livraison = "Payante"

            products.append({
                'competitor' : self.competitor_id, 
                'ref': ref.text.strip().replace("[", "").replace("]", "") if ref else "N/A",
                'url' : link.get("href"),
                'product_name': product_name.text.strip() if product_name else "Unknown",
                'product_price': product_price  if product_price else "No Price",
                'discount': discount.text.strip() if discount else "No Discount",
                'category' : category,
                'stock_status': stock_status.text.strip() if stock_status else "Epuisé",
                'description' : "",
                'livraison' : livraison,
                'image': image.get("src") if image else "No Image",
                "LastUpdate" :  datetime.now(UTC)
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
    scraper = MegaPcScraper()
    scraper.get_urls()
