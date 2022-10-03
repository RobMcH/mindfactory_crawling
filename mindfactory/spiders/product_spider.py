import json
import scrapy
import re
from mindfactory.items import MindfactoryItem, ReviewItem


class ProductSpider(scrapy.Spider):
    name = "mindfactory_products"
    with open('tech_details.json', 'w') as ff:
            tech_details_all=json.dump([],ff)
    # Start with main categories, there is no reason to start on the main page. Items on sale in Schnäppshop
    # and Mindstar are ignored since there is usually a very limited quantity of them available.
    start_urls = ['https://www.mindfactory.de/Hardware.html', 'https://www.mindfactory.de/Software.html',
                  'https://www.mindfactory.de/Notebook+~+PC.html', 'https://www.mindfactory.de/Kommunikation.html',
                  'https://www.mindfactory.de/Entertainment.html', 'https://www.mindfactory.de/Heim+~+Garten.html']
    allowed_domains = ["www.mindfactory.de"]

    def __init__(self, *args, **kwargs):
        """
        Set XPath expressions for extracting all subcategory and product links, titles, prices, reviews etc.
        """
        self.category_xpath = '//li[@class="background_maincat1"]/a/@href'
        self.product_xpath = '//a[@class="p-complete-link visible-xs visible-sm"]/@href'
        self.site_title = '/html/head/meta[@property="og:title"]/@content'
        self.next_page_xpath = '//a[@aria-label="Nächste Seite"]/@href'
        self.product_brand_xpath = '//span[@itemprop="brand"]/text()'
        self.product_ean_xpath = '//span[@class="product-ean"]/text()'
        self.product_sku_xpath = '//span[@class="sku-model"]/text()'
        self.product_price_xpath = '//span[@class="specialPriceText"]/text() |' \
                                   ' //div[@id="priceCol"]/div[@class="pprice"]/text()[3]'
        # First element is the amount of sold products; second element is the amount of people watching this product
        self.product_sold_or_people = '//*[@id="cart_quantity"]//div[@class="psold"]/text()[2]'
        self.product_count_xpath = '//*[@id="cart_quantity"]//div[@class="psold"]/span[@class="pcountsold"]/text()'
        self.shipping_xpath = '//a[@class="shipping1" or @class="shipping2" or @class="shipping3" or' \
                              ' @class="shipping4" or @class="shipping5"]/text()'
        self.product_rma_xpath = '//p[@class="mat5"]/text()'  # in percent
        self.review_xpath = '//div[@itemprop="review"]'
        # All of the review xpath are relative to the original review xpath.
        self.review_stars_xpath = 'div[1]/div/div[@class="pstars pull-left"]/' \
                                  'span[@class="glyphicon glyphicon-star filled-star"]'
        self.review_author_xpath = 'div[1]/div/div[2]/strong/text()'
        self.review_date_xpath = 'div[1]/div/div[2]/span/text()'
        self.review_verified_xpath = 'div[1]/div/div[3]/strong/span'
        self.review_text_xpath = 'div[2]/div/text()'
        super(ProductSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # Extract URLs to all subcategories.
        for href in response.xpath(self.category_xpath):
            url = href.get()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        # Extract URL to the next page.
        next_page = response.xpath(self.next_page_xpath).get()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse_category)
        # Extract URLs to all products on each page.
        category = response.xpath(self.site_title).get(default=None)
        for href in response.xpath(self.product_xpath):
            url = href.get()
            yield scrapy.Request(url, callback=self.parse_product, meta={"category": category})

    def parse_product(self, response):
        # Extract information on product page and process reviews.
        item = MindfactoryItem()
        item["url"] = response.url
        item["category"] = response.meta["category"]
        name = response.xpath(self.site_title).get(default=None)
        price_in_name = re.match("\(€.*\)", name)  # Check for malformed product names and clean them.
        if price_in_name is not None:
            name = name[price_in_name.end():]
        item["name"] = name
        item["brand"] = response.xpath(self.product_brand_xpath).get(default=None)
        item["ean"] = response.xpath(self.product_ean_xpath).get(default=None)
        item["sku"] = response.xpath(self.product_sku_xpath).get(default=None)
        price = response.xpath(self.product_price_xpath).get(default=None)
        if price is not None:
            text = price.rstrip()[1:-1]
            if text:
                item["price"] = float(text.replace("-", "0").replace(".", "").replace(",", "."))
        else:
            item["price"] = None
        count_and_people = response.xpath(self.product_count_xpath).getall()
        sold_or_people = response.xpath(self.product_sold_or_people).get(default=None)
        # Assign the amount of sold products and watching people depending on the present information.
        if len(count_and_people) == 2:
            item["count_sold"] = int(count_and_people[0].replace(".", ""))
            item["people_watching"] = int(count_and_people[1].replace(".", ""))
        elif len(count_and_people) == 1:
            item["count_sold"] = int(count_and_people[0].replace(".", "")) if sold_or_people is not None else None
            item["people_watching"] = None if sold_or_people is not None else int(count_and_people[0].replace(".", ""))
        else:
            item["count_sold"] = item["people_watching"] = None
        rma = response.xpath(self.product_rma_xpath).get(default=None)
        item["rma_quote"] = int(rma.strip()[:-1]) if rma is not None else None
        shipping = response.xpath(self.shipping_xpath).get(default=None)
        item["shipping"] = shipping.split("|")[0].strip() if shipping is not None else None
        item["reviews"], item["avg_rating"] = [], 0.0
        for review in response.xpath(self.review_xpath):
            item["reviews"].append(self.parse_review(review))
        next_page = response.xpath(self.next_page_xpath).get(default=None)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.review_helper, meta={"item": item}, dont_filter=True)
        else:
            yield item
        ############### Export tech details to JSON 
        with open('tech_details.json', 'r') as ff:
            tech_details_all=json.load(ff)
        headings=response.css('.table.table-striped.table-hover thead th::text').getall()
        tables=response.css('.table.table-striped.table-hover tbody')
        tech_details={'sku':response.xpath(self.product_sku_xpath).get(default=None)}
        for each_table in tables:
            i=tables.index(each_table)
            tech_details[headings[i]]={}
            rows=each_table.css('tr')
            for each_row in rows:
                cells=each_row.css('td::text').getall()
                label=cells[0]
                l_data=cells[1]
                tech_details[headings[i]][label]=l_data
        with open('tech_details.json', 'w') as ff:
            tech_details_all.append(tech_details)
            json.dump(tech_details_all,ff)
    def review_helper(self, response):
        # Recursively extract all reviews for a single product.
        item = response.meta["item"]
        next_page = response.xpath(self.next_page_xpath).get(default=None)
        for review in response.xpath(self.review_xpath):
            item["reviews"].append(self.parse_review(review))
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.review_helper, meta={"item": item}, dont_filter=True)
        else:
            yield item

    def parse_review(self, review):
        # Extract all present data of a single review.
        rev = ReviewItem()
        rev["stars"] = len(review.xpath(self.review_stars_xpath))
        rev["author"] = review.xpath(self.review_author_xpath).get()
        date_list = review.xpath(self.review_date_xpath).get()[3:].split(".")
        rev["date"] = f"{date_list[2]}-{date_list[1]}-{date_list[0]}"
        rev["verified"] = 1 if review.xpath(self.review_verified_xpath).get(
            default=None) is not None else 0
        text = review.xpath(self.review_text_xpath).getall()
        rev["text"] = " ".join([x.strip() for x in text])
        return rev
