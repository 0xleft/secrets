import sys
import pymongo
import config

client = pymongo.MongoClient(config.dotenv["MONGO_URI"])
db = client["secrets"]

# remove duplicated
def remove_duplicated():
    total = 0
    secrets = list(db["secrets"].find({}))
    for secret in secrets:
        count = db["secrets"].count_documents({"url": secret["url"], "commit": secret["commit"], "path": secret["path"], "secret": secret["secret"], "match": secret["match"], "rule_id": secret["rule_id"], "owner": secret["owner"], "date": secret["date"]})
        if count > 1:
            total += count - 1
            for i in range(count-1):
                db["secrets"].delete_one({"url": secret["url"], "commit": secret["commit"], "path": secret["path"], "secret": secret["secret"], "match": secret["match"], "rule_id": secret["rule_id"], "owner": secret["owner"], "date": secret["date"]})
    print(f"Removed {total} duplicated secrets")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No utils selected")
        exit(1)

    if sys.argv[1] == "rmdup":
        remove_duplicated()
        exit(0)