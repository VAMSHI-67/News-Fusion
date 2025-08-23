"""
Scrapy settings for the crawler
"""

BOT_NAME = 'newsfusion'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3

# Disable cookies
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
   'crawler.pipelines.NewsfusionPipeline': 300,
   'crawler.pipelines.GoogleNewsPipeline': 400,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Enable showing throttling stats for every response received
AUTOTHROTTLE_DEBUG = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.selectreactor.SelectReactor'

# Logging level
LOG_LEVEL = 'INFO'

# User agent settings
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Handle redirects
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 5

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Cache settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour

# Default headers
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en',
}

# Disable some extensions to reduce overhead
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
} 