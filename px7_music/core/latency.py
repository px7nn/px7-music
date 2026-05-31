import time
import urllib.request

_URLS = (
    "http://1.1.1.1",
    "https://example.com",
)

def get_latency():
    for url in _URLS:
        try:
            req   = urllib.request.Request(url, headers={"User-Agent": "px7-music"})
            start = time.perf_counter()
            urllib.request.urlopen(req, timeout=2)
            return int((time.perf_counter() - start) * 1000)
        except Exception:
            continue
    return None
