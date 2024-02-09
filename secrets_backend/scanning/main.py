from git import Repo
import scan
import hashlib
import os
import requests
from config import VERBOSE, THREAD_COUNT
import dotenvit
import threading

dotenv = dotenvit.DotEnvIt()

def scan_repo(url: str):
    should_exit = False
    try:
        repo_hash = hashlib.sha256(url.encode()).hexdigest()

        repo = Repo.clone_from(url, repo_hash)
        try:
            scan.scan_gitleaks(repo, url)
        except Exception as e:
            if VERBOSE:
                print(e)

        repo.close()
    except KeyboardInterrupt:
        should_exit = True
    except Exception as e:
        if VERBOSE:
            print(e)

    if os.name == "nt":
        os.system(f"rmdir /s /q {repo_hash}")
    else:
        os.system(f"rm -rf {repo_hash}")
    
    if should_exit:
        os.remove(f"{repo.working_dir}_gitleaks.json")
        exit(1)

def get_repos(latest_id: int):
    response = requests.get(f"https://api.github.com/repositories?since={latest_id}", headers={
        "Authorization": f"Bearer {dotenv['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json"
    })

    return response.json()

def save_latest_id(latest_id: int):
    with open("latest_id", "w+") as f:
        f.write(str(latest_id))

def get_latest_id() -> int:
    with open("latest_id", "r") as f:
        return int(f.read())

thread_count = 0
def thread_scan(url: str, thread_index: int):
    global thread_count
    thread_count += 1
    try:
        scan_repo(url)
    except Exception as e:
        if VERBOSE:
            print(e)
    thread_count -= 1

if __name__ == "__main__":
    while True:
        latest_id = get_latest_id()
        repos = get_repos(latest_id)
        print(f"Scanning {len(repos)} repositories")
        for repo in repos:
            while thread_count >= THREAD_COUNT:
                pass
            threading.Thread(target=thread_scan, args=(repo["html_url"], thread_count)).start()
        save_latest_id(repos[-1]["id"])

        while thread_count > 0:
            pass