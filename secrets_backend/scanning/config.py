import os
import dotenvit

dotenv = dotenvit.DotEnvIt("../../.env")
VERBOSE = True
GITLEAKS_BIN = './bin/gitleaks.exe' if os.name == 'nt' else './bin/gitleaks_linux'
THREAD_COUNT = 10
SHOULD_SKIP_FORKS = True
THREAD_TIMEOUT = 180