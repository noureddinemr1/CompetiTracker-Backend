import datetime
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
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
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
            print("Error: Competitor not found in the database.")
            self.competitor_id = None
            return

        self.competitor_id = competitor["_id"]
        self.chrome_driver_path = "C:\prgrms\chromedriver-win64\chromedriver-win64\chromedriver.exe"
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

            ul_element = self.driver.find_element(By.XPATH, '//*[@id="sp-vermegamenu"]/ul/li[2]/div/ul')
            soup = BeautifulSoup(ul_element.get_attribute('outerHTML'), 'html.parser')

            links = set()
            for li in soup.find_all('li'):
                a_tag = li.find('a', href=True)
                if a_tag:
                    href = a_tag['href']
                    if href != "javaScript:void(0);":
                        links.add("https://spacenet.tn"+href)

            sorted_links = sorted(links)

            if not sorted_links:
                print("No product URLs found.")
                return

            data_entry = {
                "competitor": self.competitor_id,
                "scrapedAt": datetime.datetime.utcnow(),
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
        item = url.rstrip("/").split("/")[-1]
        category = item[:len(item)-5]
        return category.replace("-", " ")


    def scrape_page(self, page_url):
        """Scrape product details from a single category page"""
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch page: {page_url} ({e})")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        products = []

        product_list = soup.find('div', class_='row')
        if not product_list:
            print(f"No products found on page: {page_url}")
            return []
        

        for item in product_list.find_all('div', class_='item col-xs-6 col-sm-4  col-md-3 col-lg-3'):
            product_name = item.find('h2', class_='product_name')
            product_price = item.find('span', class_='price').text.strip()
            #remove the letters with re
            match = re.search(r'\d+', product_price)
            price = float(match.group())
            link = item.find('a', class_="thumbnail product-thumbnail")
            stock_status = item.find('div', class_='product-quantities')
            ref = item.find('div', class_='product-reference')
            discount = item.find('span', class_='discount-amount')
            image = item.find('img', class_="img-responsive product_image")
            if price>=300 : 
                livraison = "Gratuite"
            else:
                livraison = "Payante"

            products.append({
                'url' : link.get("href"),
                'product_name': product_name.text.strip() if product_name else "Unknown",
                'product_price': product_price,
                'discount': discount.text.strip() if discount else "No Discount",
                'stock_status': stock_status.text.strip() if stock_status else "Epuisé",
                'ref': ref.text.strip().replace("[", "").replace("]", "") if ref else "N/A",
                'livraison' : livraison,
                'image': image.get("src") if image else "No Image",
            })

        return products

    def scrape_element(self, base_url):
        """Scrape all pages for a single category"""
        page_num = 1
        all_products = []
        first_page_products = None
        category = self.get_category(base_url)

        while True:
            url = f"{base_url}?p={page_num}"
            products_on_page = self.scrape_page(url,category)

            if page_num == 1:
                first_page_products = products_on_page

            if not products_on_page or (page_num > 1 and products_on_page == first_page_products):
                break

            all_products.extend(products_on_page)
            page_num += 1

        return all_products

    def scrape_all(self):
        """Main function to scrape all categories"""
        #self.get_urls()
        mytek = get_from_db("urls", {"competitor": self.competitor_id})

        if not mytek or "urls" not in mytek:
            print("No URLs found in database.")
            return

        for url in mytek["urls"]:
            print(f"Scraping: {url}")
            returned = self.scrape_element(url)
            if returned:
                save_to_db("products", returned)
            else:
                print(f"Skipping {url} due to scraping error.")


if __name__ == "__main__":
    scraper = SpacenetScraper()
    print(scraper.scrape_page("https://spacenet.tn/74-pc-portable-tunisie"))
