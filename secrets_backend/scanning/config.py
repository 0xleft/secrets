import os
import dotenvit

dotenv = dotenvit.DotEnvIt()
VERBOSE = True
GITLEAKS_BIN = './bin/gitleaks.exe' if os.name == 'nt' else './bin/gitleaks_linux'
THREAD_COUNT = 4