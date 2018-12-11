import scrapy
import scrapy.shell
from mindfactory.items import MindfactoryItem, ReviewItem


class ProductSpider(scrapy.Spider):
    name = "mindfactory_products"
    start_urls = ['https://www.mindfactory.de/Hardware.html', 'https://www.mindfactory.de/Software.html',
                  'https://www.mindfactory.de/Notebook+~+PC.html', 'https://www.mindfactory.de/Kommunikation.html',
                  'https://www.mindfactory.de/Entertainment.html', 'https://www.mindfactory.de/Heim+~+Garten.html']
    allowed_domains = ["www.mindfactory.de"]

    def __init__(self):
        """
        Set xpath for extracting all subcategory and product links, titles, prices, reviews etc.
        """
        self.category_xpath = '//li[@class="background_maincat1"]/a/@href'
        self.product_xpath = '//a[@class="p-complete-link visible-xs visible-sm"]/@href'
        self.next_page_xpath = '//a[@aria-label="Nächste Seite"]/@href'
        self.product_name_xpath = '//h1[@itemprop="name"]/text()'
        self.product_brand_xpath = '//span[@itemprop="brand"]/text()'
        self.product_ean_xpath = '//span[@class="product-ean"]/text()'
        self.product_sku_xpath = '//span[@class="sku-model"]/text()'
        self.product_sprice_xpath = '//span[@class="specialPriceText"]/text()'
        self.product_price_xpath = '//div[@id="priceCol"]/div[@class="pprice"]/text()[3]'
        # First element is the amount of sold products; second element is the amount of people watching this product
        self.product_count_xpath = '//span[@class="pcountsold"]/text()'
        self.product_rma_xpath = '//p[@class="mat5"]/text()'  # in percent
        self.review_xpath = '//div[@itemprop="review"]'
        # All of the review xpath are relative to the original review xpath.
        self.review_stars_xpath = 'div[1]/div/div[@class="pstars pull-left"]/span[@class="glyphicon glyphicon-star filled-star"]'
        self.review_author_xpath = 'div[1]/div/div[2]/strong/text()'
        self.review_date_xpath = 'div[1]/div/div[2]/span/text()'
        self.review_verified_xpath = 'div[1]/div/div[3]/strong/span'
        self.review_text_xpath = 'div[2]/div/text()'
        self.review_number_xpath_old = '//span[@class="reviewcount"]/text()'
        self.review_number_xpath_new = '//span[@itemprop="reviewCount"]/text()'
        self.reviews = []

    def parse(self, response):
        # Extract URLs to all subcategories.
        for href in response.xpath(self.category_xpath):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        # Extract URL to the next page.
        next_page = response.xpath(self.next_page_xpath).extract()
        if len(next_page) > 0:
            yield scrapy.Request(next_page[0], callback=self.parse_category)
        # Extract URLs to all products on each page.
        for href in response.xpath(self.product_xpath):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_product)

    def parse_product(self, response):
        # Extract information on product page and process reviews.
        item = MindfactoryItem()
        item["name"] = response.xpath(self.product_name_xpath).extract()[0]
        item["brand"] = response.xpath(self.product_brand_xpath).extract()[0]
        item["ean"] = response.xpath(self.product_ean_xpath).extract()[0]
        item["sku"] = response.xpath(self.product_sku_xpath).extract()[0]
        sprice = response.xpath(self.product_sprice_xpath).extract()
        price = response.xpath(self.product_price_xpath).extract()
        if len(price) > 0 and len(price[0].strip()) > 0:
            item["price"] = price[0].rstrip()[1:-1]
        elif len(sprice) > 0:
            item["price"] = sprice[0].rstrip()[1:-1]
        else:
            item["price"] = "N/A"
        count_and_people = response.xpath(self.product_count_xpath).extract()
        item["count_sold"] = count_and_people[0]
        item["people_watching"] = count_and_people[1]
        rma = response.xpath(self.product_rma_xpath).extract()
        item["rma_quote"] = rma[0].strip()[:-1] if len(rma) > 0 else "N/A"
        item["reviews"] = []
        for review in response.xpath(self.review_xpath):
            item["reviews"].append(self.parse_review(review))
        yield item

    def parse_review(self, review):
        rev = ReviewItem()
        stars = 0
        for star in review.xpath(self.review_stars_xpath):
            stars += 1
        rev["stars"] = stars
        rev["author"] = review.xpath(self.review_author_xpath).extract()[0]
        rev["date"] = review.xpath(self.review_date_xpath).extract()[0][3:]
        rev["verified"] = True if len(review.xpath(self.review_verified_xpath)) > 0 else False
        text = review.xpath(self.review_text_xpath).extract()
        if len(text) > 0:
            rev["text"] = " ".join([x.strip() for x in text])
        else:
            rev["text"] = "N/A"
        return rev
