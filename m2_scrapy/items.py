# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UpcScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    upc = scrapy.Field()
    ItemName = scrapy.Field()
    ItemSalePrice = scrapy.Field()
    Ingredients = scrapy.Field()
    ReviewStars = scrapy.Field()
    ProductDimension = scrapy.Field()
    productInfo = scrapy.Field()
    ReviewNumber = scrapy.Field()
    ASIN = scrapy.Field()
    URL = scrapy.Field()
    Time = scrapy.Field()
