from git import Repo, rmtree
import scan
import hashlib
import os
import requests
from config import VERBOSE, THREAD_COUNT, dotenv
import threading

def delete_repo(path: str):
    rmtree(path)

def scan_repo(url: str, owner: str):
    should_exit = False
    repo_hash = hashlib.sha256(url.encode()).hexdigest()

    try:
        repo = Repo.clone_from(url, f"tmp/{repo_hash}")
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

def save_latest_id(latest_id: int):
    with open("latest_id", "w+") as f:
        f.write(str(latest_id))

def get_latest_id() -> int:
    with open("latest_id", "r") as f:
        return int(f.read())

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
    while True:
        latest_id = get_latest_id()
        repos = get_repos(latest_id)
        # print(f"Scanning {len(repos)} repositories")
        for repo in repos:
            while thread_count >= THREAD_COUNT:
                pass
            threading.Thread(target=thread_scan, args=(repo["html_url"], repo["owner"]["login"], )).start()
        save_latest_id(repos[-1]["id"])

        while thread_count > 0:
            pass