class Other:
    def __init__(self, raw):
        self.subclass = raw.get("subclass")  # str

    def __str__(self):
        if not self.subclass:
            return "Other"
        return "Other ({})".format(self.subclass)
