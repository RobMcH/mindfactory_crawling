import scrapy
from mindfactory.items import MindfactoryItem, ReviewItem


class ProductSpider(scrapy.Spider):
    name = "mindfactory_products"
    start_urls = ['https://www.mindfactory.de/Hardware.html', 'https://www.mindfactory.de/Software.html',
                  'https://www.mindfactory.de/Notebook+~+PC.html', 'https://www.mindfactory.de/Kommunikation.html',
                  'https://www.mindfactory.de/Entertainment.html', 'https://www.mindfactory.de/Heim+~+Garten.html']
    allowed_domains = ["www.mindfactory.de"]

    def __init__(self, *args, **kwargs):
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
        self.product_sold_or_people = '//*[@id="cart_quantity"]/div/div[2]/div[3]/div/div/text()[2]'
        self.product_count_xpath = '//*[@id="cart_quantity"]/div/div[2]/div[3]/div/div/span/text()'
        self.product_rma_xpath = '//p[@class="mat5"]/text()'  # in percent
        self.review_xpath = '//div[@itemprop="review"]'
        # All of the review xpath are relative to the original review xpath.
        self.review_stars_xpath = 'div[1]/div/div[@class="pstars pull-left"]/span[@class="glyphicon glyphicon-star filled-star"]'
        self.review_author_xpath = 'div[1]/div/div[2]/strong/text()'
        self.review_date_xpath = 'div[1]/div/div[2]/span/text()'
        self.review_verified_xpath = 'div[1]/div/div[3]/strong/span'
        self.review_text_xpath = 'div[2]/div/text()'
        # There are two different site structures containing the number of reviews for some reason.
        self.review_number_xpath_old = '//span[@class="reviewcount"]/text()'
        self.review_number_xpath_new = '//span[@itemprop="reviewCount"]/text()'
        self.reviews = []
        super(ProductSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # Extract URLs to all subcategories.
        for href in response.xpath(self.category_xpath):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        # Extract URL to the next page.
        next_page = response.xpath(self.next_page_xpath).extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse_category)
        # Extract URLs to all products on each page.
        for href in response.xpath(self.product_xpath):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_product)

    def parse_product(self, response):
        # Extract information on product page and process reviews.
        item = MindfactoryItem()
        item["url"] = response.url
        item["name"] = response.xpath(self.product_name_xpath).extract_first()
        item["brand"] = response.xpath(self.product_brand_xpath).extract_first()
        item["ean"] = response.xpath(self.product_ean_xpath).extract_first(default=-1)
        item["sku"] = response.xpath(self.product_sku_xpath).extract_first(default=-1)
        # There are prices and special prices for some reason.
        sprice = response.xpath(self.product_sprice_xpath).extract_first(default=None)
        price = response.xpath(self.product_price_xpath).extract_first(default=None)
        if price is not None:
            text = price.rstrip()[1:-1]
            if text:
                item["price"] = float(text.replace("-", "0").replace(".", "").replace(",", "."))
        if sprice is not None:
            text = sprice.rstrip()[1:-1]
            if text:
                item["price"] = float(text.replace("-", "0").replace(".", "").replace(",", "."))
        if "price" not in item:
            item["price"] = -1
        count_and_people = response.xpath(self.product_count_xpath).extract()
        sold_or_people = response.xpath(self.product_sold_or_people).extract_first(default=None)
        if len(count_and_people) == 2:
            item["count_sold"] = int(count_and_people[0].replace(".", ""))
            item["people_watching"] = int(count_and_people[1].replace(".", ""))
        elif len(count_and_people) == 1:
            item["count_sold"] = int(count_and_people[0].replace(".", "")) if sold_or_people is not None else -1
            item["people_watching"] = -1 if sold_or_people is not None else int(count_and_people[0].replace(".", ""))
        else:
            item["count_sold"] = item["people_watching"] = -1
        rma = response.xpath(self.product_rma_xpath).extract_first(default=None)
        item["rma_quote"] = int(rma.strip()[:-1]) if rma is not None else -1
        item["reviews"] = []
        for review in response.xpath(self.review_xpath):
            item["reviews"].append(self.parse_review(review))
        next_page = response.xpath(self.next_page_xpath).extract_first(default=None)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.review_helper, meta={"item": item})
        yield item

    def review_helper(self, response):
        # Recursively extract all reviews for a single product.
        item = response.meta["item"]
        next_page_temp = response.xpath(self.next_page_xpath).extract_first(default=None)
        for review in response.xpath(self.review_xpath):
            item["reviews"].append(self.parse_review(review))
        if next_page_temp is not None:
            yield scrapy.Request(next_page_temp, callback=self.review_helper, meta={"item": item})
        yield item

    def parse_review(self, review):
        # Extract all present data of a single review.
        rev = ReviewItem()
        rev["stars"] = len(review.xpath(self.review_stars_xpath))
        rev["author"] = review.xpath(self.review_author_xpath).extract_first()
        rev["date"] = review.xpath(self.review_date_xpath).extract_first()[3:]
        rev["verified"] = "True" if review.xpath(self.review_verified_xpath).extract_first(
            default=None) is not None else "False"
        text = review.xpath(self.review_text_xpath).extract()
        rev["text"] = " ".join([x.strip() for x in text])
        return rev
