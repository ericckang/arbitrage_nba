import requests
import time

def is_proxy_working(proxy: str, timeout: float = 5.0) -> bool:
    ps = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        r = requests.get("https://www.google.com", proxies=ps, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

def clean_google_passed_proxies(
    input_file:  str = "proxy-list-raw.txt",
    output_file: str = "http_proxies.txt",
    timeout:     float = 5.0
):
    working = []
    with open(input_file, "r") as infile:
        candidates = []
        for line in infile:
            parts = line.strip().split()
            if len(parts) > 1 and parts[-1] == "+":
                candidates.append(parts[0])

    print(f"Found {len(candidates)} “+” proxies to test…")

    for i, proxy in enumerate(candidates, start=1):
        print(f"[{i}/{len(candidates)}] Testing {proxy}…", end="", flush=True)
        start = time.time()
        ok = is_proxy_working(proxy, timeout)
        elapsed = time.time() - start
        if ok:
            print(f" ✅ ({elapsed:.1f}s)")
            working.append(proxy)
        else:
            print(f" ❌ ({elapsed:.1f}s)")

    with open(output_file, "w") as outfile:
        for p in working:
            outfile.write(p + "\n")

    print(f"\nWrote {len(working)} working proxies to {output_file}")

if __name__ == "__main__":
    clean_google_passed_proxies()
