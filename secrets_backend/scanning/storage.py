import pymongo
import json
from config import VERBOSE

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["secrets"]

class Secret():
    def __init__(self, url, commit, path, secret, match):
        self.url = url
        self.commit = commit
        self.path = path # File
        self.secret = secret
        self.match = match

    def save(self):
        return mongo_db["secrets"].insert_one({
            "url": self.url,
            "commit": self.commit,
            "path": self.path,
            "secret": self.secret,
            "match": self.match
        })
    
def store(json_data: str, url: str):
    json_data = json.loads(json_data)

    for secret in json_data:
        Secret(url, secret["Commit"], secret["File"], secret["Secret"], secret["Match"]).save()

    if VERBOSE:
        print(f"Stored {len(json_data)} secrets from {url}")