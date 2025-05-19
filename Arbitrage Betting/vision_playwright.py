import os
import json
import random
import base64
import asyncio
import requests

from playwright.async_api import async_playwright
import openai

from config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

# ─── Load settings ─────────────────────────────────────────────────────────────
with open("setup.json", "r") as fp:
    cfg = json.load(fp)

HEADLESS     = cfg.get("headless", "1") == "1"
PRINT_ODDS   = cfg.get("print_odds", "0") == "1"
PROXIES_FILE = "http_proxies.txt"

BET365_URL     = (
    "https://www.az.bet365.com/"
    "?_h=hcqvfaL5kFJPXQqyVxYhOg%3D%3D&btsffd=1"
    "#/AC/B18/C20604387/D48/E1453/F10"
)
SCREENSHOT_PNG = "bet365.png"

# ─── Proxy checker ─────────────────────────────────────────────────────────────
def is_proxy_working(proxy: str) -> bool:
    try:
        ps = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r  = requests.get("https://www.google.com", proxies=ps, timeout=5)
        return r.status_code == 200
    except:
        return False

# ─── Pick a working proxy (first that passes) ─────────────────────────────────
def pick_proxy():
    if not os.path.exists(PROXIES_FILE):
        return None
    with open(PROXIES_FILE) as f:
        candidates = [L.strip() for L in f if L.strip()]
    random.shuffle(candidates)
    for p in candidates:
        if is_proxy_working(p):
            return p
    return None

# ─── 1) Capture a full-page screenshot via Playwright ──────────────────────────
async def capture_screenshot(url: str, output_path: str):
    proxy = pick_proxy()
    launch_args = {"headless": HEADLESS}
    if proxy:
        launch_args["proxy"] = {"server": f"http://{proxy}"}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_args)
        page    = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)              # wait for JS
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()

# ─── 2) Send that screenshot to GPT-4 Vision for odds extraction ────────────
def extract_odds_via_vision(image_path: str):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = (
        f"![bet365](data:image/png;base64,{img_b64})\n\n"
        "This is a Bet365 NBA lines page. Return valid JSON with a "
        "`games` array. Each entry needs:\n"
        "  • team1: name of first team\n"
        "  • team2: name of second team\n"
        "  • odds: object mapping each team name to its money-line value\n\n"
        "Example:\n"
        '{ "games": [ '
        '{ "team1":"MIN Timberwolves", "team2":"OKC Thunder", '
        '"odds": { "MIN Timberwolves":"+245", "OKC Thunder":"-305" } } '
        '] }'
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return json.loads(resp.choices[0].message.content)

# ─── Entry point ──────────────────────────────────────────────────────────────
async def main():
    await capture_screenshot(BET365_URL, SCREENSHOT_PNG)
    data = extract_odds_via_vision(SCREENSHOT_PNG)

    if PRINT_ODDS:
        print(json.dumps(data, indent=2))

    return data

if __name__ == "__main__":
    asyncio.run(main())