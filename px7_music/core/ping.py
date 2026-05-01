import urllib.request
import time

def get_ping():
    try:
        start = time.time()
        urllib.request.urlopen("https://www.google.com", timeout=3)
        return int((time.time() - start) * 1000)
    except Exception:
        return None