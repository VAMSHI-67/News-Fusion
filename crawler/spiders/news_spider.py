import scrapy
import hashlib
import datetime
import django
import os
import sys

# Add the project to the path to access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsfusion.settings')
django.setup()

from newsapp.models import NewsArticle, NewsSource


class NewsSpider(scrapy.Spider):
    name = 'news'
    
    def __init__(self, *args, keyword=None, source_id=None, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword  # For keyword-based search
        self.source_id = source_id  # To limit to a specific source
        
        # Set start_urls based on active sources
        if source_id:
            sources = NewsSource.objects.filter(is_active=True, id=source_id)
        else:
            sources = NewsSource.objects.filter(is_active=True)
        
        self.start_urls = [source.url for source in sources]
        self.source_map = {source.url: source for source in sources}
    
    def parse(self, response):
        # Example parser for Times of India
        if 'timesofindia.indiatimes.com' in response.url:
            return self.parse_toi(response)
        # Example parser for The Hindu
        elif 'thehindu.com' in response.url:
            return self.parse_hindu(response)
        else:
            self.logger.info(f"No parser for {response.url}")
            
    def parse_toi(self, response):
        source = self.get_source(response.url)
        
        # Times of India article selectors
        articles = response.css('div.card-container')
        
        for article in articles:
            headline = article.css('h2 a::text').get()
            url = article.css('h2 a::attr(href)').get()
            summary = article.css('p.card-txt::text').get() or headline
            
            # Apply keyword filter if specified
            if self.keyword and self.keyword.lower() not in headline.lower() and self.keyword.lower() not in summary.lower():
                continue
                
            # Create content hash
            content = (headline + summary).encode('utf-8')
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Check if article already exists
            if not NewsArticle.objects.filter(content_hash=content_hash).exists():
                # Save to database
                NewsArticle.objects.create(
                    source=source,
                    headline=headline,
                    summary=summary,
                    url=url,
                    content_hash=content_hash
                )
    
    def parse_hindu(self, response):
        source = self.get_source(response.url)
        
        # The Hindu article selectors
        articles = response.css('div.story-card')
        
        for article in articles:
            headline = article.css('h3 a::text').get()
            url = article.css('h3 a::attr(href)').get()
            # Adjust based on actual HTML structure
            summary = article.css('p.intro::text').get() or headline
            
            # Apply keyword filter if specified
            if self.keyword and self.keyword.lower() not in headline.lower() and self.keyword.lower() not in summary.lower():
                continue
                
            # Create content hash
            content = (headline + summary).encode('utf-8')
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Check if article already exists
            if not NewsArticle.objects.filter(content_hash=content_hash).exists():
                # Save to database
                NewsArticle.objects.create(
                    source=source,
                    headline=headline,
                    summary=summary,
                    url=url,
                    content_hash=content_hash
                )
    
    def get_source(self, url):
        for base_url, source in self.source_map.items():
            if base_url in url:
                return source
        return None 