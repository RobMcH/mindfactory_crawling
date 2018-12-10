import scrapy


class ProductSpider(scrapy.Spider):
    name = "mindfactory_products"
    start_urls = ['https://www.mindfactory.de/Hardware.html', 'https://www.mindfactory.de/Software.html',
                  'https://www.mindfactory.de/Notebook+~+PC.html', 'https://www.mindfactory.de/Kommunikation.html',
                  'https://www.mindfactory.de/Entertainment.html', 'https://www.mindfactory.de/Heim+~+Garten.html']
    allowed_domains = ["https://www.mindfactory.de/"]

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
        self.product_price_xpath = '//span[@class="specialPriceText"]/text()'  # ['\xa0128,49*']
        # First element is the amount of sold products; second element is the amount of people watching this product
        self.product_count_xpath = '//span[@class="pcountsold"]/text()'
        self.product_rma_xpath = '//p[@class="mat5"]/text()'  # in percent

    def parse(self, response):
        pass
        #TODO
