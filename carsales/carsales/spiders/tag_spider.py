import scrapy


class TagSpider(scrapy.Spider):
    name = "tags"

    def start_requests(self):
        url = f'http://quotes.toscrape.com/tag/{self.tag}'
        # tag = getattr(self, 'tag', None)
        # if tag is not None:
        # url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
