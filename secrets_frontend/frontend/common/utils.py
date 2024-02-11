import hashlib  
import random

def generate_api_key():
    return hashlib.sha256(str(random.getrandbits(4096)).encode()).hexdigest()