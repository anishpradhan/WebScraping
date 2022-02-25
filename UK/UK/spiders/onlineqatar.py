import scrapy
from requests_html import HTMLSession
import re

class QatarSpider(scrapy.Spider):
    name = "qatar_1"
    # urls = ['https://www.qataryello.com/category/Small_business/'+str(i) for i in range(2,10)]
    start_urls = [
        'https://www.onlineqatar.com/directory'
    ]

    def parse(self, response, **kwargs):
        companies = response.css('h3.content_list_box_title a::attr(href)').getall()

        for urls in companies:
            url = 'https://www.onlineqatar.com' + urls
            yield scrapy.Request(url, callback=self.parse_company)

    def parse_company(self, response):
        name = response.css('h1.common_h1 span::text').get()
        address = response.css('span.itm_directory_add span::text').get()
        phone = response.css('span.itm_directory_contact span::text').get()
        email = response.css('span.itm_directory_email a::text').get()
        website = response.css('span.itm_directory_web a::attr(href)').get()

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
            'email': clean_list,
            'emails': email
        }