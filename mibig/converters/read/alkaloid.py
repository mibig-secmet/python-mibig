class Alkaloid:
    def __init__(self, raw):
        self.subclass = raw.get("subclass")  # str

    def __str__(self):
        if not self.subclass:
            return "Alkaloid"
        return "Alkaloid ({})".format(self.subclass)
