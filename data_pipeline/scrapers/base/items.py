import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    url = scrapy.Field()
    website = scrapy.Field()
    category = scrapy.Field()
    timestamp = scrapy.Field()
    metadata = scrapy.Field()