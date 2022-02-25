import scrapy, requests
import random
import time
import re
from ..items import UkItem
import sys
from requests_html import HTMLSession


class CarDetail(scrapy.Spider):
    name = 'it'
    allowed_domains = ['themanifest.com']

    def start_requests(self):
            urls = ['https://themanifest.com/au/it-services/companies']
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        all_item = response.css('div.view-content:nth-child(2) > div:nth-child(1)')
        for data in all_item:
            company_name = data.css('header h3[class="text-uppercase title"] a::text').getall()
            # company_location = data.css('div.provider-basics-item-label span[class="comp-addr"] span::text').getall()
            link = data.css('div.profile-visit a::attr(href)').getall()
            EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
            session = HTMLSession()
            i=0
            while i!= len(link)-1:
                r = session.get(link[i])
                r.html.render()
                email_list = []
                for re_match in re.finditer(EMAIL_REGEX, r.html.raw_html.decode()):
                    company_email = re_match.group()
                    email_list.append(company_email)

                clean_email_set = set(email_list)
                clean_list = list(clean_email_set)
                individual_company_name = company_name[i]
                item = UkItem()
                item['company_Name'] = individual_company_name
                item['company_Email'] = clean_list
                item['company_website_link']=link[i]
                yield item
                i+=1


    # def parse_car(self, response, **kwargs):
    #     print('sucessfully called this function')
    #     link_get = response.meta['url']
    #     url = link_get
    #     company_name = response.meta['company_name']
    #     # company_location = response.meta('company_location')
    #     print(link_get, 'here is the link')
    #     print(company_name, 'here is the name')



