from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from testTask.spiders.alkoteka_spider import FirstSpiderSpider

if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(FirstSpiderSpider)
    process.start()