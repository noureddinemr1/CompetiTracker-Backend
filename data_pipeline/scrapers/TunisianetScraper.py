from datetime import datetime, UTC
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os



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

class TunisianetScraper:
    def __init__(self):
        self.url = "https://www.tunisianet.com.tn/"
        competitor = get_from_db("competitors", {"url": self.url})

        if not competitor:
            data ={
                "name": "Tunisianet",
                "url": self.url,
                "logo": "https://www.tunisianet.com.tn/img/tunisianet-logo-1611064619.jpg",
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
            return None
        
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(4)

            ul_element = self.driver.find_element(By.XPATH, '//*[@id="_desktop_top_menu"]/div/div/ul/li[1]')
            soup = BeautifulSoup(ul_element.get_attribute('outerHTML'), 'html.parser')
            

            # Extract links from the ul_element
            links = set()
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if href != "javaScript:void(0);":
                    links.add(href)

            sorted_links = sorted(links)

            data_entry = {
                "competitor": self.competitor_id,
                "scrapedAt" : datetime.datetime.utcnow(),
                "urls" : sorted_links
            }
            save_to_db("urls",data_entry)

        except Exception as e:
            print(f"Error occurred during scraping: {e}")
            return None
        finally:
            self.driver.quit()
        




    def get_category(self, url):
        """Extract category from URL and replace dashes with spaces"""
        item = url.rstrip("/").split("/")[-1]
        category = item[3:]
        return category.replace("-", " ")


    def scrape_page(self, page_url,category):
        """Scrape product details from a single category page"""
        try:
            response = requests.get(page_url)
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

        for item in product_list.find_all('div', class_='item-product'):
            product_name = item.find('h2', class_='h3 product-title')
            product_price = item.find('span', class_='price').text.strip()
            #remove the letters with re
            price_cleaned = re.sub(r'[^\d,]', '', product_price)  # Remove everything except digits and commas
            price = float(price_cleaned.replace(',', '.').replace(" ",""))
            link = item.find('a', class_="thumbnail product-thumbnail first-img")
            stock_status = item.find('div', id='stock_availability')
            ref = item.find('span', class_='product-reference')
            description = item.find('div' , class_="listds")
            discount = item.find('span', class_='discount-amount discount-product')
            image = item.find('img', class_="center-block img-responsive")
            if price>=300 : 
                livraison = "Gratuite"
            else:
                livraison = "Payante"

            products.append({
                "competitor" : self.competitor_id,                
                'url' : link.get("href"),
                'product_name': product_name.text.strip() if product_name else "Unknown",
                'product_price': product_price,
                'discount': discount.text.strip() if discount else "No Discount",
                'category' : category,
                'stock_status': stock_status.text.strip() if stock_status else "Epuisé",
                'ref': ref.text.strip().replace("[", "").replace("]", "") if ref else "N/A",
                'description': description.text.strip() if description else "N/A",
                'livraison' : livraison,
                'image': image.get("src") if image else "No Image",
                "LastUpdate" : datetime.now(UTC)
           })
            print(product_name.text.strip())

        return products
   

    def scrape_element(self, base_url):
        """Scrape all pages for a single category"""
        page_num = 1
        all_products = []
        category = self.get_category(base_url)

        while True:
            url = f"{base_url}?page={page_num}"
            soup = BeautifulSoup(requests.get(url).content, 'lxml')
            next_button = soup.find('a', class_='next js-search-link')
            if not next_button : break
            products_on_page = self.scrape_page(url,category)
            if not products_on_page : 

                products_on_page = self.scrape_page2(url,category)
            all_products.extend(products_on_page)
            page_num += 1
        return all_products
    
    def get_product_id(self,url):
        product = get_from_db("products",{"url" : url})
        return product["_id"]


    def scrape_all(self):
        """Main function to scrape all categories"""
        #self.get_urls()
        tunisianet = get_from_db("urls", {"competitor": self.competitor_id})

        if not tunisianet or "urls" not in tunisianet:
            print("No URLs found in database.")
            return

        for url in tunisianet["urls"]:
            print(f"Scraping: {url}")
            returned = self.scrape_element(url)

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
    scraper = TunisianetScraper()
    scraper.scrape_all()
