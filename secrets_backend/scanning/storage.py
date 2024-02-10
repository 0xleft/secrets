import pymongo
import json
from config import VERBOSE, dotenv

mongo_client = pymongo.MongoClient(dotenv["MONGO_URI"])
mongo_db = mongo_client["secrets"]

def save_latest_id(latest_id: int):
    return mongo_db["info"].update_one({}, {"$set": {"latest_id": latest_id}}, upsert=True)

def get_latest_id() -> int:
    obj = mongo_db["info"].find_one()
    if obj is None:
        return 0
    return obj["latest_id"]

class Secret():
    def __init__(self, url, commit, path, secret, match, rule_id, owner, date):
        self.url = url
        self.commit = commit
        self.path = path # File
        self.secret = secret
        self.match = match
        self.rule_id = rule_id
        self.owner = owner
        self.date = date

    def save(self):
        return mongo_db["secrets"].insert_one({
            "url": self.url,
            "commit": self.commit,
            "path": self.path,
            "secret": self.secret,
            "match": self.match,
            "rule_id": self.rule_id,
            "owner": self.owner,
            "date": self.date
        })
    
def store(json_data: str, url: str, owner: str):
    json_data = json.loads(json_data)

    for secret in json_data:
        Secret(url, secret["Commit"], secret["File"], secret["Secret"], secret["Match"], secret["RuleID"], owner, secret["Date"]).save()

    if VERBOSE:
        print(f"Stored {len(json_data)} secrets from {url}")