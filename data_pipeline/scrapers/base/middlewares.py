from urllib.parse import urlparse
from random import choice
from scrapy import signals

class CustomProxyMiddleware:
    def process_request(self, request, spider):
        if not request.meta.get('proxy'):
            request.meta['proxy'] = spider.proxy_manager.get_random_proxy()

class DomainLimitMiddleware:
    def __init__(self, max_pages_per_domain=100):
        self.max_pages = max_pages_per_domain
        self.domain_counts = {}

    def process_request(self, request, spider):
        domain = urlparse(request.url).netloc
        self.domain_counts[domain] = self.domain_counts.get(domain, 0) + 1
        
        if self.domain_counts[domain] > self.max_pages:
            spider.logger.info(f"Reached max pages for domain: {domain}")
            raise scrapy.exceptions.IgnoreRequest()