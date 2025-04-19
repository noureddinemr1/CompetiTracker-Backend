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

class ScoopGamingScraper:
    def __init__(self):
        self.url = "https://www.scoopgaming.com.tn/"
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

            ul_element = self.driver.find_element(By.XPATH, '//*[@class="menu-content"]')
            soup = BeautifulSoup(ul_element.get_attribute('outerHTML'), 'html.parser')

            links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href != "javaScript:void(0);" and href.count("/") == 5:
                    links.add(href)

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
        
        # Remove .html if it exists
        if item.endswith(".html"):
            item = item[:-5]
        
        # Remove leading numbers and dash (e.g., '46-' or '123-')
        parts = item.split("-", 1)
        if parts[0].isdigit() and len(parts) > 1:
            item = parts[1]
        
        return item.replace("-", " ")



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

        product_list = soup.find('div', class_='products')
        if not product_list:
            print(f"No products found on page: {page_url}")
            return []

        for item in product_list.find_all('article', class_='item'):
            product_name = item.find('div', class_='tvproduct-name product-title')
            product_price = item.find('span', class_='price').text.strip()
            #remove the letters with re
            match = re.search(r'\d+', product_price)
            price = float(match.group())
            link = item.find('a', class_="thumbnail product-thumbnail")
            
            stock_status = item.find('div', class_='disponible-category')
            if not stock_status:
                stock_status = item.find('div', class_='stock available available_backorder')
            ref = item.find('div', class_='skuDesktop')
            description = item.find('div' , class_="description")
            discount = item.find('span', class_='discount-price')
            image = item.find('img', class_="product-image-photo")
            """""
            garantie_element = soup.find("strong", string=lambda text: text and "Garantie" in text)
            if garantie_element : 
                garantie = garantie_element.text.strip().replace("Garantie:", "").strip()
            """""
            if price>=300 : 
                livraison = "Gratuite"
            else:
                livraison = "Payante"

            products.append({
                'url' : link.get("href"),
                'product_name': product_name.text.strip() if product_name else "Unknown",
                'product_price': product_price,
                'discount': discount.text.strip() if discount else "No Discount",
                'category' : category,
                'stock_status': stock_status.text.strip() if stock_status else "Epuisé",
                'ref': ref.text.strip().replace("[", "").replace("]", "") if ref else "N/A",
                'description': description.text.strip() if description else "N/A",
                'garantie' : "Sans Garantie",
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
                save_to_db("mytek_products", returned)
            else:
                print(f"Skipping {url} due to scraping error.")


if __name__ == "__main__":
    scraper = ScoopGamingScraper()
    scraper.scrape_all()
