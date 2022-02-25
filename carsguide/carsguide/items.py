# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CarsguideItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    car_names = scrapy.Field()

class AventadorItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    about = scrapy.Field()

