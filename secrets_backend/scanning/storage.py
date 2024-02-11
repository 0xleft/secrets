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

def add_repo_count(repos: int):
    return mongo_db["info"].update_one({}, {"$inc": {"repo_count": repos}}, upsert=True)

def add_secret_count(secrets: int):
    return mongo_db["info"].update_one({}, {"$inc": {"secret_count": secrets}}, upsert=True)

class Secret():
    def __init__(self, url, commit, path, secret, match, rule_id, owner, date, requester):
        self.url = url
        self.commit = commit
        self.path = path # File
        self.secret = secret
        self.match = match
        self.rule_id = rule_id
        self.owner = owner
        self.date = date
        self.requester = requester

    def save(self):
        if self.requester is not None:
            # add to scan object secret array
            return mongo_db["scans"].update_one({"url": self.url, "user_id": int(self.requester)}, {
                "$push": {
                    "secrets": {
                        "commit": self.commit,
                        "path": self.path,
                        "secret": self.secret,
                        "match": self.match,
                        "rule_id": self.rule_id,
                        "owner": self.owner,
                        "date": self.date
                    }
                },
            }, upsert=True)
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

    
def store(json_data: str, url: str, owner: str, requester: str):
    json_data = json.loads(json_data)

    for secret in json_data:
        Secret(url, secret["Commit"], secret["File"], secret["Secret"], secret["Match"], secret["RuleID"], owner, secret["Date"], requester).save()

    if requester is not None:
        mongo_db["scans"].update_one({"url": url, "user_id": int(requester)}, {"$set": {"status": "done"}})

    if requester is None:
        add_secret_count(len(json_data))

    if VERBOSE:
        print(f"Stored {len(json_data)} secrets from {url}")