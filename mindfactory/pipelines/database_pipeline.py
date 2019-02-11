import sqlite3
import time


class DatabasePipeline(object):
    def __init__(self):
        db_name = f"./mindfactory-{time.time()}.db"
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        # Create tables for product and review data.
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS productdata
                            (
                              id              INTEGER PRIMARY KEY,
                              url             TEXT NOT NULL,
                              category        TEXT,
                              name            TEXT,
                              brand           TEXT,
                              ean             CHAR(13),
                              sku             TEXT,
                              count_sold      INTEGER,
                              people_watching INTEGER,
                              shipping        VARCHAR(20),
                              rma_quote       INTEGER,
                              price           REAL,
                              avg_rating      REAL
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reviewdata
                            (
                              product_id  INTEGER REFERENCES productdata (id) NOT NULL,
                              stars       INTEGER,
                              review_text TEXT,
                              author      TEXT,
                              date        TEXT,
                              verified    BIT
                            )""")
        # Create search indices.
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS url_index ON productdata(url)")
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS id_index ON productdata(id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS pid_index ON reviewdata(product_id)")
        self.connection.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.execute("""
                              INSERT INTO productdata
                              (url, category, name, brand, ean, sku, count_sold, people_watching, shipping, rma_quote,
                               price, avg_rating)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (item["url"], item["category"], item["name"], item["brand"], item["ean"], item["sku"],
                             item["count_sold"], item["people_watching"], item["shipping"], item["rma_quote"],
                             item["price"], item["avg_rating"]))
        row_id = self.cursor.lastrowid
        for rev in item["reviews"]:
            self.cursor.execute("""INSERT INTO reviewdata VALUES (?, ?, ?, ?, ?, ?)""",
                                (row_id, rev["stars"], rev["text"], rev["author"], rev["date"], rev["verified"]))
        self.connection.commit()
        return item

    def handle_error(self, e):
        # Next level error handling.
        pass
