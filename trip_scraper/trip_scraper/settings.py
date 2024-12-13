# Scrapy settings for trip_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "trip_scraper"

SPIDER_MODULES = ["trip_scraper.spiders"]
NEWSPIDER_MODULE = "trip_scraper.spiders"

# Enable logging for debugging
LOG_LEVEL = 'DEBUG'
# Delay between requests
DOWNLOAD_DELAY = 5  # 3 seconds (adjust as needed)

# Enable randomization of delay
RANDOMIZE_DOWNLOAD_DELAY = True

# Concurrent requests settings
CONCURRENT_REQUESTS = 1  # Optional: Reduce concurrency for gentler scraping
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# Custom User-Agent
USER_AGENT = 'trip_hotel_scraper (https://yourwebsite.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"



