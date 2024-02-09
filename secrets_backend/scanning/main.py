from git import Repo
import scan
import hashlib
import os

class Scan():
    pass

def scan_repo(url: str):
    repo_hash = hashlib.sha256(url.encode()).hexdigest()

    repo = Repo.clone_from(url, repo_hash)
    try:
        scan.scan_gitleaks(repo, url)
    except:
        pass

    repo.close()
    if os.name == 'nt':
        os.system(f"rmdir /s /q {repo_hash}")
    else:
        os.system(f"rm -rf {repo_hash}")

if __name__ == '__main__':
    scan_repo('https://github.com/vidaud/seta')