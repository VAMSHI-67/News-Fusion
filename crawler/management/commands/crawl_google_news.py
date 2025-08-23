from django.core.management.base import BaseCommand
from crawler.google_news_crawler import GoogleNewsCrawlerThread
from newsapp.models import Article
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Google News crawler to fetch articles'

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Keyword to search for')
        parser.add_argument('--wait', action='store_true', help='Wait for the crawler to finish')
        parser.add_argument('--max-wait', type=int, default=180, help='Maximum time to wait in seconds (default: 180)')

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        wait = options.get('wait', False)
        max_wait = options.get('max_wait', 180)
        
        # Get initial article count
        initial_count = Article.objects.count()
        initial_keyword_count = 0
        if keyword:
            initial_keyword_count = Article.objects.filter(keyword=keyword).count()
            self.stdout.write(f'Starting crawler for keyword: "{keyword}"')
            self.stdout.write(f'Initial articles with keyword "{keyword}": {initial_keyword_count}')
        else:
            self.stdout.write('Starting crawler for trending news')
        
        self.stdout.write(f'Initial article count: {initial_count}')
        
        try:
            # Start the crawler thread
            crawler_thread = GoogleNewsCrawlerThread(keyword=keyword)
            crawler_thread.start()
            
            if wait:
                # Wait for the crawler thread to finish or timeout
                self.stdout.write('Waiting for crawler to finish...')
                wait_time = 0
                while crawler_thread.is_alive() and wait_time < max_wait:
                    if wait_time % 10 == 0:  # Print status every 10 seconds
                        self.stdout.write(f'Crawler running for {wait_time} seconds...')
                    time.sleep(1)
                    wait_time += 1
                
                # Check if crawler is still running
                if crawler_thread.is_alive():
                    self.stdout.write(self.style.WARNING(
                        f'Crawler still running after {max_wait} seconds. Continuing in background.'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS('Crawler completed successfully!'))
            else:
                self.stdout.write('Crawler started in background. Use --wait option to wait for completion.')
                
            # Show stats even if not waiting, though numbers may be incomplete
            current_count = Article.objects.count()
            new_articles = current_count - initial_count
            
            self.stdout.write(f'Current article count: {current_count}')
            self.stdout.write(f'New articles added: {new_articles}')
            
            if keyword:
                current_keyword_count = Article.objects.filter(keyword=keyword).count()
                keyword_articles_added = current_keyword_count - initial_keyword_count
                self.stdout.write(f'Articles with keyword "{keyword}": {current_keyword_count}')
                self.stdout.write(f'New articles for keyword "{keyword}": {keyword_articles_added}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running crawler: {str(e)}'))
            raise 