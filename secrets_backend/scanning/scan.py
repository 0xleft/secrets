from git import Repo
import subprocess
import os
import storage

GITLEAKS_BIN = './bin/gitleaks'

def scan_gitleaks(repo: Repo, url: str):
    subprocess.run([GITLEAKS_BIN, 'detect', '-s', repo.working_dir, '--exit-code', '0', '--no-banner', '--no-color', '--report-format', 'json', '--log-level', 'error', '--report-path', f'{repo.working_dir}_gitleaks.json', '--verbose'], stderr=subprocess.DEVNULL, check=True)


    with open(f'{repo.working_dir}_gitleaks.json', 'r') as f:
        print(f.read())
        storage.store(f.read(), url)

    os.remove(f'{repo.working_dir}_gitleaks.json')