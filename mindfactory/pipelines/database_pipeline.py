import sqlite3


class DatabasePipeline(object):

    def __init__(self):
        self.connection = sqlite3.connect('./scrapedata.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS productdata (id INTEGER PRIMARY KEY, url TEXT, category TEXT,
                                name TEXT, brand TEXT, ean INTEGER, sku TEXT, count_sold INTEGER, people_watching INTEGER,
                                 rma_quote INTEGER, price REAL)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reviewdata (product_id INTEGER, stars INTEGER,
        review_text TEXT, author TEXT, date TEXT, verified TEXT)""")

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.execute("""INSERT INTO productdata (url, category, name, brand, ean, sku, count_sold,
             people_watching, rma_quote, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (item["url"], item["category"],
                             item["name"], item["brand"], item["ean"], item["sku"], item["count_sold"],
                             item["people_watching"],
                             item["rma_quote"], item["price"]))
        row_id = self.cursor.lastrowid
        for review in item["reviews"]:
            self.cursor.execute("""INSERT INTO reviewdata VALUES (?, ?, ?, ?, ?, ?)""",
                                (row_id, review["stars"], review["text"], review["author"], review["date"],
                                 review["verified"]))
        self.connection.commit()
        return item

    def handle_error(self, e):
        # Next level error handling
        pass
