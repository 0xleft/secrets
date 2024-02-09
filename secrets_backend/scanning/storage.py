import pymongo
import json
from config import VERBOSE, dotenv

mongo_client = pymongo.MongoClient(dotenv["MONGO_URI"])
mongo_db = mongo_client["secrets"]

class Secret():
    def __init__(self, url, commit, path, secret, match, rule_id, owner):
        self.url = url
        self.commit = commit
        self.path = path # File
        self.secret = secret
        self.match = match
        self.rule_id = rule_id
        self.owner = owner

    def save(self):
        return mongo_db["secrets"].insert_one({
            "url": self.url,
            "commit": self.commit,
            "path": self.path,
            "secret": self.secret,
            "match": self.match,
            "rule_id": self.rule_id,
            "owner": self.owner
        })
    
def store(json_data: str, url: str, owner: str):
    json_data = json.loads(json_data)

    for secret in json_data:
        Secret(url, secret["Commit"], secret["File"], secret["Secret"], secret["Match"], secret["RuleID"], owner).save()

    if VERBOSE:
        print(f"Stored {len(json_data)} secrets from {url}")