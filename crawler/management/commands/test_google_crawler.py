from django.core.management.base import BaseCommand
from crawler.google_news_crawler import GoogleNewsCrawlerThread
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test the Google News crawler with the new implementation'

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Keyword to search for')
        parser.add_argument('--timeout', type=int, default=30, help='Maximum time to wait (seconds)')

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        timeout = options.get('timeout', 30)
        
        if keyword:
            self.stdout.write(f'Testing Google News crawler for keyword: {keyword}')
        else:
            self.stdout.write('Testing Google News crawler for trending news')
        
        try:
            # Start the crawler thread
            crawler_thread = GoogleNewsCrawlerThread(keyword=keyword)
            crawler_thread.start()
            
            # Wait for the crawler thread to finish or timeout
            wait_time = 0
            while crawler_thread.is_alive() and wait_time < timeout:
                self.stdout.write(f'Crawler running ({wait_time}s)...')
                time.sleep(1)
                wait_time += 1
            
            if crawler_thread.is_alive():
                self.stdout.write(self.style.WARNING(f'Crawler still running after {timeout} seconds. This is normal if it\'s fetching a lot of data.'))
                self.stdout.write('The crawler will continue running in the background.')
            else:
                self.stdout.write(self.style.SUCCESS('Crawler completed successfully!'))
                
            # Show import statistics
            from newsapp.models import Article
            article_count = Article.objects.count()
            self.stdout.write(f'Current article count in database: {article_count}')
            
            if keyword:
                keyword_articles = Article.objects.filter(keyword=keyword).count()
                self.stdout.write(f'Articles with keyword "{keyword}": {keyword_articles}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running crawler: {str(e)}'))
            raise 