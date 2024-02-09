import pymongo
import json

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['secrets']

class Secret():
    def __init__(self, url, commit, path, secret):
        self.url = url
        self.commit = commit
        self.path = path
        self.secret = secret

    def save(self):
        return mongo_db['secrets'].insert_one({
            'url': self.url,
            'commit': self.commit,
            'path': self.path,
            'secret': self.secret
        })
    
def store(json_data: str, url: str):
    json_data = json.loads(json_data)

    for secret in json_data:
        Secret(url, json_data["commit"], json_data['file'], json_data['secret']).save()