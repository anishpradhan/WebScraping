import scrapy


class Carsales(scrapy.Spider):
    name = "carsales"

    def start_requests(self):
        url = 'https://www.carsales.com.au/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
        }
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
        yield scrapy.Request(url, self.parse, headers=headers)

    def parse(self, response, **kwargs):
        yield {
            # 'title': response.css('h1.title::text').get(),
            'title': 'CARSALES',
        }
