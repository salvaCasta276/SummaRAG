import scrapy
import os, json
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
        item["title"] = ''.join(response.css('h1.PostsPageTitle-root a.PostsPageTitle-link ::text').getall()).strip()
        item["author"] = response.css('.PostsAuthors-authorName a.UsersNameDisplay-noColor::text').get()
        item["date"] = response.css('time::attr(datetime)').get()
        item["content"] = ' '.join(response.css('#postContent .InlineReactSelectionWrapper-root ::text').getall()).strip()

        self.write_json(item)
        yield item

    def write_json(self, item):
        # Create a directory for the output if it doesn't exist
        if not os.path.exists('output'):
            os.makedirs('output')

        # Create a filename based on the title extract from the url
        title = item["url"].split('/')[-1]

        # Write the item to a json file
        with open(f'output/{title}.json', 'w') as f:
            json.dump(dict(item), f, indent=4)
        