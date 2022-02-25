import scrapy


class AuthorSpider(scrapy.Spider):
    name = "author"

    start_urls = [
        'http://quotes.toscrape.com'
    ]

    def parse(self, response, **kwargs):
        # quote1 = response.css('div.quote')[0]
        author_link = response.css('.author+ a')
        yield from response.follow_all(author_link, self.parse_author)

    def parse_author(self, response, **kwargs):
        yield {
            'Author Name': response.css('h3.author-title::text').get(default='').strip(),
            'Born Date': response.css('span.author-born-date::text').get(default='').strip(),
            'Born Location': response.css('span.author-born-location::text').get(default='').strip(),
            'Description': response.css('.author-description::text').get(default='').strip()
        }
