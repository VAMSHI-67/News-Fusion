from django.core.management.base import BaseCommand
from crawler.crawler_api import run_crawler, NewsCrawler
from newsapp.models import NewsSource
import time

class Command(BaseCommand):
    help = 'Crawl news from configured sources'

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Keyword to search for')
        parser.add_argument('--source_id', type=int, help='ID of the source to crawl')
        parser.add_argument('--wait', action='store_true', help='Wait for crawler to finish')

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        source_id = options.get('source_id')
        wait = options.get('wait', False)
        
        # Check if there are active sources
        if not NewsSource.objects.filter(is_active=True).exists():
            self.stdout.write(self.style.WARNING('No active news sources found. Please add some in the admin panel.'))
            return
            
        # Run the crawler
        if keyword:
            self.stdout.write(f'Crawling news for keyword: {keyword}')
        else:
            self.stdout.write('Crawling trending news')
            
        if wait:
            # Run synchronously if wait is specified
            crawler = NewsCrawler(keyword=keyword, source_id=source_id)
            crawler.start()
            self.stdout.write('Crawler running, please wait...')
            
            # Wait for crawler to finish (maximum 3 minutes)
            max_wait = 180  # seconds
            while crawler.is_alive() and max_wait > 0:
                time.sleep(1)
                max_wait -= 1
                
            if crawler.is_alive():
                self.stdout.write(self.style.WARNING('Crawler still running after timeout. Continuing in background.'))
            else:
                self.stdout.write(self.style.SUCCESS('Crawling completed'))
        else:
            # Run asynchronously
            run_crawler(keyword=keyword, source_id=source_id)
            self.stdout.write(self.style.SUCCESS('Crawler started successfully (running in background)')) 