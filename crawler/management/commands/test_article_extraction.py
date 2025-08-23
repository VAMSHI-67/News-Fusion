from django.core.management.base import BaseCommand
import scrapy
import logging
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess
from crawler.spiders.google_news_spider import GoogleNewsSpider
from scrapy import signals
from scrapy.signalmanager import dispatcher
from pprint import pprint

# Configure logging
configure_logging(install_root_handler=False)
logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TestGoogleNewsSpider(GoogleNewsSpider):
    """A test version of the GoogleNewsSpider that doesn't save items to the database"""
    name = 'test_google_news'
    
    custom_settings = {
        'ITEM_PIPELINES': {},  # Disable pipelines to avoid saving to DB
        'LOG_LEVEL': 'INFO',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 2,  # Be nice to Google News
    }
    
    def __init__(self, keyword=None, max_items=5, *args, **kwargs):
        super(TestGoogleNewsSpider, self).__init__(keyword=keyword, *args, **kwargs)
        self.items = []
        self.max_items = max_items  # Limit to max_items for the test
        
    def parse(self, response):
        """Override parse to collect items and stop after max_items"""
        for item in super(TestGoogleNewsSpider, self).parse(response):
            self.items.append(item)
            yield item
            
            # Stop after collecting max_items
            if len(self.items) >= self.max_items:
                raise scrapy.exceptions.CloseSpider(reason='Collected enough items')

class Command(BaseCommand):
    help = 'Test article extraction from Google News without saving to the database'

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Keyword to search for')
        parser.add_argument('--count', type=int, default=5, help='Number of articles to extract (default: 5)')

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        count = options.get('count', 5)
        
        if keyword:
            self.stdout.write(f'Testing article extraction for keyword: "{keyword}"')
        else:
            self.stdout.write('Testing article extraction for trending news')
        
        # Items will be stored here
        items = []
        
        def crawler_results(signal, sender, item, response, spider):
            items.append(item)
            
        # Connect the signal to capture items
        dispatcher.connect(crawler_results, signal=signals.item_scraped)
        
        # Configure the crawler process
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'LOG_LEVEL': 'INFO'
        })
        
        # Start the crawler with the spider class, not an instance
        self.stdout.write('Starting crawler...')
        process.crawl(TestGoogleNewsSpider, keyword=keyword, max_items=count)
        process.start()  # This will block until the crawling is finished
        
        # Display the results
        self.stdout.write(self.style.SUCCESS(f'Extracted {len(items)} articles:'))
        
        for i, item in enumerate(items, 1):
            self.stdout.write(f"\n{i}. {item['title']}")
            self.stdout.write(f"   URL: {item['url']}")
            self.stdout.write(f"   Source: {item['source']}")
            self.stdout.write(f"   Published: {item['published_time']}")
            if item.get('summary'):
                self.stdout.write(f"   Summary: {item['summary']}")
            self.stdout.write(f"   Keyword: {item.get('keyword', 'None')}")
        
        self.stdout.write(self.style.SUCCESS('\nTest completed successfully!')) 