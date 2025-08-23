import scrapy
import hashlib
import re
import logging
import traceback
from urllib.parse import urlencode, urlparse, parse_qs
from ..items import GoogleNewsItem

logger = logging.getLogger(__name__)

class GoogleNewsSpider(scrapy.Spider):
    name = 'google_news'
    allowed_domains = ['news.google.com']
    
    # Custom settings for this spider
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.GoogleNewsPipeline': 400,
        },
        'LOG_LEVEL': 'DEBUG',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    def __init__(self, keyword=None, *args, **kwargs):
        super(GoogleNewsSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        
        # Build the start URL based on keyword or use trending news
        if keyword:
            params = {'q': keyword, 'hl': 'en-IN', 'gl': 'IN', 'ceid': 'IN:en'}
            self.start_urls = [f'https://news.google.com/search?{urlencode(params)}']
        else:
            self.start_urls = ['https://news.google.com/topstories?hl=en-IN&gl=IN&ceid=IN:en']
        
        logger.info(f"Initialized spider with start URLs: {self.start_urls}")
    
    def parse(self, response):
        """
        Parse Google News search results or top stories page
        """
        logger.info(f"Parsing response from: {response.url}")
        
        # Google News articles are in article elements with various classes
        articles = response.css('article.IBr9hb, article.UwIKyb, article.IFHyqb')
        logger.info(f"Found {len(articles)} articles on page")
        
        article_count = 0
        error_count = 0
        
        for i, article in enumerate(articles):
            try:
                # Log the article we're working on
                logger.debug(f"Processing article #{i+1}")
                
                # Extract article title - look for title in multiple possible locations
                title_selectors = [
                    'h3 a::text', 
                    'h4 a::text', 
                    'a.DY5T1d::text', 
                    'a[class*="aqvwYd"]::text', 
                    'a::text'
                ]
                
                title = None
                for selector in title_selectors:
                    title = article.css(selector).get()
                    if title:
                        break
                
                if not title:
                    logger.debug(f"Article #{i+1} has no title, skipping")
                    continue
                
                logger.debug(f"Article #{i+1} title: {title}")
                
                # Extract summary if available - try multiple possible selectors
                summary_selectors = [
                    'span[class*="xBbh9"]::text',
                    'div.Da10Tb::text',
                    'div[class*="Rai5ob"]::text',
                    'div.QNKWqe::text'
                ]
                
                summary = None
                for selector in summary_selectors:
                    summary = article.css(selector).get()
                    if summary:
                        break
                
                # Extract article URL (convert from relative to absolute)
                url_selectors = [
                    'h3 a::attr(href)',
                    'h4 a::attr(href)',
                    'a.DY5T1d::attr(href)',
                    'a[class*="aqvwYd"]::attr(href)',
                    'a::attr(href)'
                ]
                
                relative_url = None
                for selector in url_selectors:
                    relative_url = article.css(selector).get()
                    if relative_url:
                        break
                        
                if not relative_url:
                    logger.debug(f"Article #{i+1} has no URL, skipping")
                    continue
                
                logger.debug(f"Article #{i+1} relative URL: {relative_url}")
                
                # Google News URLs are relative paths that start with "./" - join with response URL
                article_url = response.urljoin(relative_url)
                
                # Get the real URL by removing Google's redirect
                real_url = self.get_real_article_url(article_url)
                logger.debug(f"Article #{i+1} real URL: {real_url}")
                
                # Extract source name
                source_selectors = [
                    'div[class*="vr1PYe"] a::text',
                    'div.QNKWqe span::text',
                    'div.UOVeFe::text',
                    'div.SVJrMe a::text'
                ]
                
                source = None
                for selector in source_selectors:
                    source = article.css(selector).get()
                    if source:
                        break
                
                if not source:
                    source = "Google News"
                
                # Extract published time
                time_selectors = [
                    'div[class*="SVJrMe"] time::text',
                    'time::text',
                    'div.kvVbwb::text'
                ]
                
                published_time = None
                for selector in time_selectors:
                    published_time = article.css(selector).get()
                    if published_time:
                        break
                        
                if not published_time:
                    published_time = "Recent"
                
                # Create a new item
                item = GoogleNewsItem()
                item['title'] = title.strip()
                item['summary'] = summary.strip() if summary else ""
                item['url'] = real_url
                item['source'] = source.strip()
                item['published_time'] = published_time.strip()
                item['keyword'] = self.keyword
                
                # Create content hash
                content = (item['title'] + item['url']).encode('utf-8')
                item['content_hash'] = hashlib.sha256(content).hexdigest()
                
                logger.info(f"Yielding article: {item['title']}")
                article_count += 1
                yield item
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing article #{i+1}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Processed {article_count} articles from this page, {error_count} errors")
            
        # Follow pagination links if available
        next_page_selectors = [
            'a[class*="VfPpkd-BIzmGd"]::attr(href)',
            'a[class*="jKHa4e"]::attr(href)',
            'a[jsname="sCfAK"][role="menuitem"]::attr(href)'
        ]
        
        next_page = None
        for selector in next_page_selectors:
            next_page = response.css(selector).get()
            if next_page:
                break
                
        if next_page:
            logger.info(f"Following pagination to next page: {next_page}")
            yield response.follow(next_page, self.parse)
        else:
            logger.info("No pagination links found, ending crawl")
            
    def get_real_article_url(self, google_url):
        """
        Extract the real article URL from Google's redirect URL
        """
        try:
            parsed = urlparse(google_url)
            if '/articles/' in parsed.path:
                return google_url
                
            # Extract the 'url' query parameter if present
            query_params = parse_qs(parsed.query)
            if 'url' in query_params:
                return query_params['url'][0]
        except Exception as e:
            logger.error(f"Error extracting URL: {str(e)}")
            
        return google_url 