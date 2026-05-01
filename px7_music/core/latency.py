import urllib.request, time

def get_latency():
    urls = [
        "http://1.1.1.1",        
        "https://example.com",  
    ]

    for url in urls:
        try:
            start = time.perf_counter()

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "px7-music"}
            )

            urllib.request.urlopen(req, timeout=2)

            return int((time.perf_counter() - start) * 1000)

        except Exception:
            continue

    return None