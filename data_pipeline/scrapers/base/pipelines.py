import logging
from itemadapter import ItemAdapter

class DataValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if not adapter.get('name'):
            raise scrapy.exceptions.DropItem("Missing product name")
            
        if not adapter.get('price'):
            raise scrapy.exceptions.DropItem("Missing product price")
            
        if not adapter.get('url'):
            raise scrapy.exceptions.DropItem("Missing product URL")
            
        return item

class DataStoragePipeline:
    def open_spider(self, spider):
        self.logger = logging.getLogger(spider.name)
        # Initialize storage connection here (DB, S3, etc.)

    def close_spider(self, spider):
        # Close storage connection
        pass

    def process_item(self, item, spider):
        # Implement storage logic
        self.logger.info(f"Storing product: {item['name']}")
        return item