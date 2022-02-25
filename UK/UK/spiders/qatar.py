import scrapy
from requests_html import HTMLSession
import re

class QatarSpider(scrapy.Spider):
    name = "qatar"
    urls = ['https://www.kuwaityello.com/category/Small_business/'+str(i) for i in range(1,54)]
    start_urls = urls

    def parse(self, response, **kwargs):
        comp_list = response.css('div#listings')
        companies = comp_list.xpath('//div[contains(@class, "g_0")]/h4/a/@href').extract()

        for url in companies:
            url = 'https://www.kuwaityello.com' + url
            yield scrapy.Request(url, callback=self.parse_company)

    def parse_company(self, response):
        name = response.css('b#company_name::text').get()
        address = ''.join([i for i in response.css('div.text.location::text, div.text.location a.city530::text').getall()])
        phone = response.css('div.text.phone::text').getall()
        website = response.css('.text.weblinks a::attr(href)').get()
        if website:

            # EMAIL SCRAPING
            EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
            session = HTMLSession()
            r = session.get(website)
            r.html.render()
            email_list = []
            for re_match in re.finditer(EMAIL_REGEX, r.html.raw_html.decode()):
                company_email = re_match.group()
                email_list.append(company_email)

            clean_email_set = set(email_list)
            clean_list = list(clean_email_set)
        else:
            clean_list = None
        yield {
            'company_name': name,
            'address': address,
            'phone_number': phone,
            'url': website,
            'email': clean_list
        }