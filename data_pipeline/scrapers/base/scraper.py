import scrapy
from scrapy import signals
from scrapy.exceptions import CloseSpider
from ..utils.proxy_rotation import ProxyRotation
from ..utils.data_normalizer import DataNormalizer

class BaseProductScraper(scrapy.Spider):
    name = "base_product_scraper"
    allowed_domains = []
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 2,
        'RETRY_TIMES': 3,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_manager = ProxyRotation()
        self.normalizer = DataNormalizer()
        self.products_collected = 0
        self.max_products = kwargs.get('max_products', 1000)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        self.logger.info(f"Spider closed: {spider.name}")
        self.logger.info(f"Total products collected: {self.products_collected}")

    def start_requests(self):
        raise NotImplementedError("Subclasses must implement start_requests")

    def parse_product(self, response):
        raise NotImplementedError("Subclasses must implement parse_product")

    def should_collect_more(self):
        return self.products_collected < self.max_products