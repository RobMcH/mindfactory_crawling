from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):
    """
    Removes already processed items from the pipeline.
    """

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        url = item["url"]
        if url in self.seen_urls:
            raise DropItem(f"Duplicate item found with URL {url}")
        else:
            self.seen_urls.add(url)
            return item
