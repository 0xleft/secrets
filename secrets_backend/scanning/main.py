from git import Repo, rmtree
import scan
import hashlib
import os
import requests
from config import VERBOSE, THREAD_COUNT, dotenv, SHOULD_SKIP_FORKS
import threading
import storage
import sys
# 131391033

def delete_repo(path: str):
    rmtree(path)

def scan_repo(url: str, owner: str):
    should_exit = False
    repo_hash = hashlib.sha256(url.encode()).hexdigest()

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
        scan.scan_gitleaks(repo, url, owner)
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
def thread_scan(url: str, owner: str):
    global thread_count
    thread_count += 1
    try:
        scan_repo(url, owner)
    except Exception as e:
        if VERBOSE:
            print(e)
    thread_count -= 1

if __name__ == "__main__":
    # get first argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            storage.mongo_db.drop_collection("secrets")
            storage.save_latest_id(int(sys.argv[2]))
            exit(0)

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