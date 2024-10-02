from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ainewscraper.spiders.alignment import AlignmentSpider

def run_spider():
    settings = get_project_settings()
    settings['LOG_LEVEL'] = 'INFO'
    settings['DOWNLOAD_DELAY'] = 1
    settings['CONCURRENT_REQUESTS'] = 1
    
    process = CrawlerProcess(settings)
    process.crawl(AlignmentSpider)
    process.start()

if __name__ == "__main__":
    run_spider()