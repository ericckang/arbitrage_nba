import uuid
import time
import requests

from config import OXYLABS_USERNAME, OXYLABS_PASSWORD, PROXIES_ENDPOINT

OUTPUT_FILE  = "http_proxies.txt"
LOCATION_URL = "https://ip.oxylabs.io/location"
NUM_PROXIES  = 10        # unique proxies
DELAY_SEC    = 0.5       # pause between attempts

def test_proxy(username: str, password: str):
    proxy_url = f"http://{username}:{password}@{PROXIES_ENDPOINT}"
    proxies   = {"http": proxy_url, "https": proxy_url}
    try:
        r = requests.get(LOCATION_URL, proxies=proxies, timeout=10)
        r.raise_for_status()
        ip = r.json().get("ip")
        return True, ip
    except Exception:
        return False, None

def generate_proxies(count: int):
    sessions = []
    while len(sessions) < count:
        sid  = uuid.uuid4().hex
        user = f"{OXYLABS_USERNAME}-sessid-{sid}"
        ok, ip = test_proxy(user, OXYLABS_PASSWORD)
        if ok:
            line = f"{user}:{OXYLABS_PASSWORD}@{PROXIES_ENDPOINT}"
            sessions.append(line)
            print(f"[✓] Session {sid} → IP {ip}")
        else:
            print(f"[✗] Session {sid} failed")
        time.sleep(DELAY_SEC)
    return sessions

def main():
    proxies = generate_proxies(NUM_PROXIES)
    with open(OUTPUT_FILE, "w") as f:
        for p in proxies:
            f.write(p + "\n")
    print(f"\nSaved {len(proxies)} proxies to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()