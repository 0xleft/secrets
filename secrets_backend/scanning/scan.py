from git import Repo
import subprocess
import os
import storage
from config import VERBOSE, GITLEAKS_BIN

def is_safe(dir: str):
    for char in dir:
        if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_.\\:/":
            return False
    return True

def scan_gitleaks(repo: Repo, url: str, owner: str, requester):

    if not is_safe(repo.working_dir):
        raise Exception(f"Invalid directory name {repo.working_dir}!")

    subprocess.run([GITLEAKS_BIN, "detect", "-s", repo.working_dir, "--exit-code", "0", "--no-banner", "--no-color", "--report-format", "json", "--log-level", "error", "--report-path", f"{repo.working_dir}_gitleaks.json", "--max-target-megabytes", "1"], stderr=subprocess.DEVNULL, check=True)

    try:
        with open(f"{repo.working_dir}_gitleaks.json", "r") as f:
            storage.store(f.read(), url, owner, requester)
    except Exception as e:
        if VERBOSE:
            print(e)

    # this is because we want to delete the file even if it fails to store
    os.remove(f"{repo.working_dir}_gitleaks.json")