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

class MytekScraper:
    def __init__(self):
        self.url = "https://www.mytek.tn/"
        competitor = get_from_db("competitors", {"url": self.url})

        if not competitor:
            data ={
                "name": "Mytek",
                "url": self.url,
                "logo": "https://mk-media.mytek.tn/media/logo/stores/1/LOGO-MYTEK-176PX-INVERSE.png",
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
                li_xpath = f'//*[@id="rw-menutop"]/li[1]/div/ul/li[{i}]'
                li_element = self.driver.find_element(By.XPATH, li_xpath)
                soup = BeautifulSoup(li_element.get_attribute('outerHTML'), 'html.parser')

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
        category = item[:len(item)-5]
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

        product_list = soup.find('ol', class_='products list items product-items')
        if not product_list:
            print(f"No products found on page: {page_url}")
            return []

        for item in product_list.find_all('li', class_='product-item'):
            product_name = item.find('strong', class_='product name product-item-name')
            product_price = item.find('span', class_='price').text.strip()
            #remove the letters with re
            match = re.search(r'\d+', product_price)
            price = float(match.group())
            link = item.find('a', class_="product-item-link")
            stock_status = item.find('div', class_='card-body')
            ref = item.find('div', class_='skuDesktop')
            description = item.find('div' , class_="product description product-item-description")
            discount = item.find('span', class_='discount-price')
            image = item.find('img', class_="product-image-photo")
            if price>=300 : 
                livraison = "Gratuite"
            else:
                livraison = "Payante"

            products.append({
                'competitor' : self.competitor_id,    
                'ref': ref.text.strip().replace("[", "").replace("]", "") if ref else "N/A",
                'url' : link.get("href"),
                'product_name': product_name.text.strip() if product_name else "Unknown",
                'product_price': product_price,
                'discount': discount.text.strip() if discount else "No Discount",
                'category' : category,
                'stock_status': stock_status.text.strip() if stock_status else "Epuisé",
                'description': description.text.strip() if description else "N/A",
                'livraison' : livraison,
                'image': image.get("src") if image else "No Image",
                "LastUpdate" : datetime.datetime.utcnow()
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
    scraper = MytekScraper()
    scraper.scrape_all()
