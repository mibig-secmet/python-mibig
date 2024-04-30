from .cluster import Cluster

class Everything:
    def __init__(self, raw):
        self.cluster = Cluster(raw["cluster"])
        self.changelog = [Change(log) for log in raw["changelog"]]
        self.comments = raw.get("comments")  # str


class Change:
    def __init__(self, raw):
        self.comments = raw.get("comments")  # list[str]
        self.contributors = raw.get("contributors")  # list[str]
        self.mibig_version = raw.get("version")
        self.timestamps = raw.get("updated_at") # list[str]
        if self.mibig_version == "next":
            return
        for part in self.mibig_version.split("."):
            int(part)
