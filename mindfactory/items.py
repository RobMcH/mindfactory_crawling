import scrapy


class ReviewItem(scrapy.Item):
    """
    Item for storing a single review.
    """
    url = scrapy.Field()
    stars = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    verified = scrapy.Field()


class MindfactoryItem(scrapy.Item):
    """
    Item for storing all information about a product.
    """
    url = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    ean = scrapy.Field()
    sku = scrapy.Field()
    count_sold = scrapy.Field()
    people_watching = scrapy.Field()
    rma_quote = scrapy.Field()
    shipping = scrapy.Field()
    price = scrapy.Field()
    reviews = scrapy.Field()
    avg_rating = scrapy.Field()
