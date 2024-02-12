from git import Repo, rmtree
import scan
import hashlib
import os
import requests
from config import VERBOSE, THREAD_COUNT, dotenv, SHOULD_SKIP_FORKS
import threading
import storage
import sys
from storage import mongo_db
import time
# 131391033

def delete_repo(path: str):
    rmtree(path)

def scan_repo(url: str, owner: str, requester=None):
    should_exit = False
    to_hash = url
    if requester is not None:
        to_hash += requester
    repo_hash = hashlib.sha256(to_hash.encode()).hexdigest()

    try:
        repo = Repo.clone_from(url, f"tmp/{repo_hash}", multi_options=["--filter=blob:limit=1m"], env={"GIT_TERMINAL_PROMPT": "0"})
    except KeyboardInterrupt:
        should_exit = True
    except Exception as e:
        delete_repo(f"tmp/{repo_hash}")
        if VERBOSE:
            print(e)
        return
    try:
        scan.scan_gitleaks(repo, url, owner, requester)
    except Exception as e:
        if VERBOSE:
            print(e)

    repo.close()
    delete_repo(repo.working_dir)

    if should_exit:
        os.remove(f"{repo.working_dir}_gitleaks.json")
        exit(1)

def get_repos(latest_id: int):
    response = requests.get(f"https://api.github.com/repositories?since={latest_id}", headers={
        "Authorization": f"Bearer {dotenv['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "https://pageup.lt/ @0xleft"
    })

    return response.json()

thread_count = 0
def thread_scan(url: str, owner: str, requester=None):
    global thread_count
    thread_count += 1
    try:
        scan_repo(url, owner, requester)
    except Exception as e:
        if VERBOSE:
            print(e)
    thread_count -= 1

if __name__ == "__main__":
    # get first argument
    service = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            storage.mongo_db.drop_collection("secrets")
            storage.save_latest_id(int(sys.argv[2]))
            exit(0)
        if sys.argv[1] == "service":
            service = True
    if not service:
        while True:
            latest_id = storage.get_latest_id()
            repos = get_repos(latest_id)
            # print(f"Scanning {len(repos)} repositories")
            for repo in repos:
                if repo["fork"] and SHOULD_SKIP_FORKS:
                    continue
                while thread_count >= THREAD_COUNT:
                    pass
                threading.Thread(target=thread_scan, args=(repo["html_url"], repo["owner"]["login"], )).start()
                storage.save_latest_id(repo["id"])

            storage.add_repo_count(len(repos))

            while thread_count > 0:
                pass
    else:
        while True:
            request_scan = mongo_db["scans"].find_one({"status": "pending"})
            if request_scan is not None:
                while thread_count >= THREAD_COUNT:
                    pass
                threading.Thread(target=thread_scan, args=(request_scan["url"], "unknown", str(request_scan["user_id"]))).start()

            time.sleep(0.1)