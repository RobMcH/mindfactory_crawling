from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):
    """
    Removes already processed items from the pipeline.
    """

    def __init__(self):
        self.seen_eans = set()

    def process_item(self, item, spider):
        ean = item["ean"]
        if ean in self.seen_eans:
            raise DropItem(f"Duplicate item found with EAN {ean}")
        else:
            self.seen_eans.add(ean)
            return item
