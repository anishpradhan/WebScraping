import scrapy
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from requests_html import HTMLSession


class SamSpider(scrapy.Spider):
    name = "australia"
    start_urls = [
        'https://www.savvysme.com.au/business'
    ]

    def parse(self, response, **kwargs):
        item = response.css('div#business_category_list')
        item_cat = item.css('div.item-cat')
        for i in item_cat[17:]:
            category = i.css("div.category-item-box.animateclass.noselect::text").get().strip()
            cat_id = i.css("div.category-item-box.animateclass.noselect::attr(data-target)").get().strip('#')
            sub_cat_urls = i.css(f'div#{cat_id} div.well a::attr(href)').get()
            detail = {
                'category': category,
            }
            url = 'https://www.savvysme.com.au' + sub_cat_urls
            # print(url)
            request = scrapy.Request(url, callback=self.parse_categ, meta={'detail': detail})
            # print(request)
            yield request

    def parse_categ(self, response):
        companies = response.css('h2.business-title a::attr(href)').getall()
        print(companies)