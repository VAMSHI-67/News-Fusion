"""
Module for running the Google News crawler from Django views
"""
import threading
import logging
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from .spiders.google_news_spider import GoogleNewsSpider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to keep track of crawler states
crawler_states = {}

class GoogleNewsCrawlerThread(threading.Thread):
    """Thread class for running Scrapy crawler in the background"""
    
    def __init__(self, keyword=None):
        threading.Thread.__init__(self)
        self.keyword = keyword
        self.runner = CrawlerRunner(get_project_settings())
        self.daemon = True  # Daemon thread will be terminated when main thread exits
        
    def run(self):
        """Run the crawler process"""
        try:
            # Configure logging for this thread
            configure_logging()
            
            # Create a key for this crawler
            crawler_key = f"crawler_{self.keyword}_{id(self)}"
            crawler_states[crawler_key] = "running"
            
            # Define a callback for when the spider closes
            def on_spider_closed(spider):
                logger.info(f"Spider closed: {spider.name}")
                crawler_states[crawler_key] = "completed"
                
                # Check if any other crawlers are running
                running_crawlers = [k for k, v in crawler_states.items() if v == "running"]
                if not running_crawlers:
                    try:
                        # Only stop the reactor if it's running
                        if reactor.running:
                            reactor.stop()
                    except Exception as e:
                        logger.error(f"Error stopping reactor: {str(e)}")
            
            # Start the crawler
            deferred = self.runner.crawl(GoogleNewsSpider, keyword=self.keyword)
            deferred.addCallback(on_spider_closed)
            
            # Start the reactor in this thread if it's not running
            if not reactor.running:
                reactor.run(installSignalHandlers=False)  # Don't install signal handlers
                
            logger.info(f"Finished crawling for keyword: {self.keyword or 'trending'}")
        except Exception as e:
            logger.error(f"Error in crawler process: {str(e)}")

def run_google_news_crawler(keyword=None):
    """
    Start a Google News crawler in a separate thread
    
    Args:
        keyword (str, optional): Keyword to search for. If None, crawls trending news.
    
    Returns:
        str: Message indicating crawler was started
    """
    try:
        crawler_thread = GoogleNewsCrawlerThread(keyword=keyword)
        crawler_thread.start()
        logger.info(f"Started Google News crawler with keyword: {keyword or 'trending'}")
        return f"Started crawling Google News for {keyword or 'trending news'}"
    except Exception as e:
        logger.error(f"Failed to start crawler: {str(e)}")
        return f"Error starting crawler: {str(e)}" 