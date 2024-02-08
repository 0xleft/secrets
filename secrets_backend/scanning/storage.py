import pymongo

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['secrets']

class Secret():
    def __init__(self, repo_name, commit, path, secret):
        self.repo_name = repo_name
        self.commit = commit
        self.path = path
        self.secret = secret

    def save(self):
        return mongo_db['secrets'].insert_one({
            'repo_name': self.repo_name,
            'commit': self.commit,
            'path': self.path,
            'secret': self.secret
        })