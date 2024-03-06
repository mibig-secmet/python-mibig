from collections import OrderedDict


class Alkaloid:
    def __init__(self, subclass: str = None):
        self.subclass = subclass

    def to_json(self):
        result = OrderedDict()
        if self.subclass:
            result["subclass"] = self.subclass
        return result
