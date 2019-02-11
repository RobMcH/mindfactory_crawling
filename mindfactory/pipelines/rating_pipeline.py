class RatingPipeline(object):
    """
    Calculates the average rating of a product based on all its reviews.
    """

    def process_item(self, item, spider):
        total_stars = 0
        for review in item["reviews"]:
            total_stars += review["stars"]
        item["avg_rating"] = round(total_stars / len(item["reviews"]), 3) if item["reviews"] else None
        return item
