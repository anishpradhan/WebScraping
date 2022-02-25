# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UkItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company_Name = scrapy.Field()
    company_Email = scrapy.Field()
    company_website_link = scrapy.Field()

