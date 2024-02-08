from git import Repo
import scan

class Scan():
    pass

def scan_repo(url: str):
    repo = Repo.clone_from(url, 'temp')

    scan.scan_gitleaks(repo)
    repo.close()

if __name__ == '__main__':
    scan_repo('https://github.com/0xleft/rl_configs')