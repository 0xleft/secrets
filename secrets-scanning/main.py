from git import Repo
from . import scan

class Scan():
    pass

def scan_repo(url: str):
    repo = Repo.clone_from(url, 'temp')

    scan.scan_gitleaks(repo)

    repo.close()