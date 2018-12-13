import sqlite3
from scrapy import log


class DatabasePipeline(object):

    def __init__(self):
        self.connection = sqlite3.connect('./scrapedata.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS myscrapedata (url TEXT,'
                            ' name TEXT, brand TEXT, ean INTEGER, sku TEXT, count_sold INTEGER,'
                            ' people_watching INTEGER, rma_quote INTEGER, price REAL, reviews BLOB)')

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.executemany('INSERT INTO myscrapedata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (item["url"],
                                                                                                   item["name"], item["brand"], item["ean"], item["sku"], item["count_sold"],
                                                                                                   item[
                                                                                                       "people_watching"],
                                                                                                   item["rma_quote"],
                                                                                                   item["price"],
                                                                                                   item["reviews"]))
        self.connection.commit()
        log.msg("Item stored : " % item, level=log.DEBUG)
        return item

    def handle_error(self, e):
        log.err(e)
