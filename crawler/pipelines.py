"""
Item pipeline for processing scraped news articles
"""
import hashlib
import django
import os
import sys
import logging
from django.db import transaction

# Configure logging
logger = logging.getLogger(__name__)

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsfusion.settings')
django.setup()

from newsapp.models import NewsArticle, NewsSource, Article

class NewsfusionPipeline:
    """
    Pipeline for processing news articles
    """
    def process_item(self, item, spider):
        """
        Process each news article:
        - Check for duplicates using content hash
        - Save to database
        """
        # Create hash from headline + summary to check for duplicates
        content = (item['headline'] + item['summary']).encode('utf-8')
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Check if article already exists
        if not NewsArticle.objects.filter(content_hash=content_hash).exists():
            # Get the source
            source = spider.get_source(item['source_url'])
            if source:
                # Save to database
                NewsArticle.objects.create(
                    source=source,
                    headline=item['headline'],
                    summary=item['summary'],
                    url=item['url'],
                    content_hash=content_hash
                )
        
        return item

class GoogleNewsPipeline:
    """
    Pipeline for processing Google News articles
    """
    def __init__(self):
        self.new_articles_count = 0
        self.items_seen = set()
    
    def open_spider(self, spider):
        """Called when the spider is opened"""
        logger.info(f"Google News spider started with keyword: {spider.keyword or 'trending'}")
    
    def process_item(self, item, spider):
        """
        Process each Google News article:
        - Check for duplicates using content hash
        - Save to database
        """
        try:
            # Check if item has required fields
            if not item.get('title') or not item.get('url'):
                logger.warning("Skipping item without title or URL")
                return item
                
            # Check if article already exists by content hash
            content_hash = item.get('content_hash')
            if not content_hash:
                # Create hash if not provided
                content = (item['title'] + item['url']).encode('utf-8')
                content_hash = hashlib.sha256(content).hexdigest()
                item['content_hash'] = content_hash
            
            # Skip if we've already seen this item in this crawl
            if content_hash in self.items_seen:
                logger.debug(f"Skipping duplicate item: {item['title']}")
                return item
                
            self.items_seen.add(content_hash)
            
            # Use a transaction to avoid race conditions
            with transaction.atomic():
                # Skip if article already exists in database
                if Article.objects.filter(content_hash=content_hash).exists():
                    logger.debug(f"Article already exists in database: {item['title']}")
                    return item
                    
                # Create new article
                Article.objects.create(
                    title=item['title'],
                    summary=item.get('summary', ''),
                    url=item['url'],
                    source=item.get('source', 'Unknown'),
                    published_time=item.get('published_time', ''),
                    keyword=item.get('keyword', ''),
                    content_hash=content_hash
                )
                self.new_articles_count += 1
                logger.info(f"Saved article #{self.new_articles_count}: {item['title']}")
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
                
        return item
        
    def close_spider(self, spider):
        """
        Called when spider finishes
        """
        logger.info(f"Google News spider closed, added {self.new_articles_count} new articles to the database")
        if hasattr(spider, 'crawler') and hasattr(spider.crawler, 'stats'):
            spider.crawler.stats.set_value('new_articles_count', self.new_articles_count) 