# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewItem(scrapy.Item):
    stars = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    verified = scrapy.Field()


class MindfactoryItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    ean = scrapy.Field()
    sku = scrapy.Field()
    count_sold = scrapy.Field()
    people_watching = scrapy.Field()
    rma_quote = scrapy.Field()
    price = scrapy.Field()
    reviews = ReviewItem()
