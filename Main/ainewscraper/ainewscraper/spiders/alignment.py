import scrapy
from ainewscraper.items import AinewscraperItem


class AlignmentSpider(scrapy.Spider):
    name = "alignment"
    allowed_domains = ["alignmentforum.org"]
    start_urls = ["https://alignmentforum.org"]

    def parse(self, response):
        news = response.css("div.LWPostsItem-row")
        for new in news:
            url = new.css("a").attrib["href"]
            yield response.follow(url, callback=self.parse_new)

    def parse_new(self, response):
        item = AinewscraperItem()
        
        item["url"] = response.url
        item["title"] = ''.join(response.css('h1.PostsPageTitle-root a.PostsPageTitle-link ::text').getall()).strip(),
        item["author"] = response.css('.PostsAuthors-authorName a.UsersNameDisplay-noColor::text').get(),
        item["date"] = response.css('time::attr(datetime)').get(),
        item["content"] = ' '.join(response.css('#postContent .InlineReactSelectionWrapper-root ::text').getall()).strip()
        yield item
