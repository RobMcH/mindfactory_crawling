import sqlite3


class DatabasePipeline(object):
    def __init__(self):
        self.connection = sqlite3.connect('./scrapedata.db')
        self.cursor = self.connection.cursor()
        # If this returns None, the table does not exist. In this case INSERT instead of UPDATE is used when processing
        # items.
        self.mode = self.cursor.execute("""
                                        SELECT name FROM sqlite_master
                                        WHERE type='table' AND name='productdata'
                                        """).fetchone()
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
                              rma_quote       INTEGER,
                              price           REAL
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
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS url_index ON productdata(url)")
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS id_index ON productdata(id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS pid_index ON reviewdata(product_id)")
        self.connection.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        # Either insert items, iff the scraper is run for the first time, or update their entries.
        present = self.cursor.execute(f"SELECT id FROM productdata WHERE url = (?)", (item["url"],)).fetchone()
        if not (self.mode and present):
            self.cursor.execute("""
                                INSERT INTO productdata
                                (url, category, name, brand, ean, sku, count_sold, people_watching, rma_quote, price)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (item["url"], item["category"], item["name"], item["brand"], item["ean"], item["sku"],
                                 item["count_sold"], item["people_watching"], item["rma_quote"], item["price"]))
        else:
            self.cursor.execute(f"""
                                UPDATE productdata
                                SET count_sold = (?),
                                    people_watching = (?),
                                    rma_quote = (?),
                                    price = (?)
                                WHERE url = (?)
                                """, (item['count_sold'], item['people_watching'], item['rma_quote'], item['price'],
                                      item["url"]))
        row_id = self.cursor.lastrowid
        for rev in item["reviews"]:
            # Only insert reviews that are not yet present in the database.
            if not self.cursor.execute(f"""
                                        SELECT verified from reviewdata
                                        WHERE author = (?)
                                        AND date = (?)
                                        """, (rev["author"], rev["date"])).fetchone():
                self.cursor.execute("""INSERT INTO reviewdata VALUES (?, ?, ?, ?, ?, ?)""",
                                    (row_id, rev["stars"], rev["text"], rev["author"], rev["date"], rev["verified"]))
        self.connection.commit()
        return item

    def handle_error(self, e):
        # Next level error handling.
        pass
