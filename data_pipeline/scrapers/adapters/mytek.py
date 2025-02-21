# data_pipeline/scrapers/adapters/mytek.py
import scrapy
from ..base.items import ProductItem
from datetime import datetime

class MytekScraper(scrapy.Spider):
    name = "mytek_scraper"
    allowed_domains = ['mytek.tn']
    
    def start_requests(self):
        urls = [
            'https://www.mytek.tn/',
            # Add more category URLs
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.css('div.product-container')
        for product in products:
            if not self.should_collect_more():
                break
                
            item = ProductItem()
            item['name'] = product.css('h5.product-title::text').get()
            item['price'] = self.normalizer.normalize_price(
                product.css('span.price::text').get()
            )
            item['currency'] = self.normalizer.normalize_currency(
                product.css('span.currency::text').get()
            )
            item['url'] = response.urljoin(
                product.css('a::attr(href)').get()
            )
            item['website'] = 'Mytek'
            item['timestamp'] = datetime.now().isoformat()
            
            self.products_collected += 1
            yield item