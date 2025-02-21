# data_pipeline/scrapers/run_scrapers.py
import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Import your scrapers
from .adapters.tunisianet import TunisianetScraper
from .adapters.mytek import MytekScraper

def configure_logging():
    """Configure logging for the scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraping.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_scrapers_to_run():
    """Return list of scrapers to run with their configurations"""
    return [
        {
            'scraper': TunisianetScraper,
            'kwargs': {
                'max_products': 1000,
                'category': 'electronics'
            }
        },
        {
            'scraper': MytekScraper,
            'kwargs': {
                'max_products': 1000,
                'category': 'computers'
            }
        }
    ]

def run_spiders():
    """Main function to run all configured spiders"""
    configure_logging()
    logger = logging.getLogger(__name__)
    
    try:
        process = CrawlerProcess(get_project_settings())
        
        for scraper_config in get_scrapers_to_run():
            scraper_class = scraper_config['scraper']
            scraper_kwargs = scraper_config.get('kwargs', {})
            
            logger.info(f"Starting scraper: {scraper_class.name}")
            process.crawl(scraper_class, **scraper_kwargs)
        
        logger.info("Starting scraping process...")
        process.start()
        logger.info("Scraping completed successfully")
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_spiders()