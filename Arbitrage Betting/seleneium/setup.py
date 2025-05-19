# setup.py

import os
import json
import random
import asyncio

from playwright.async_api import async_playwright

# ─── Load configuration ───────────────────────────────────────────────────────
with open("setup.json", "r") as fp:
    cfg = json.load(fp)

CHROMEDRIVER = cfg.get("chromedriver_location")
HEADLESS     = cfg.get("headless", "1") == "1"
PRINT_ODDS   = cfg.get("print_odds", "0") == "1"
PROXIES_FILE = "http_proxies.txt"

# ─── Proxy test ────────────────────────────────────────────────────────────────
def is_proxy_working(proxy: str) -> bool:
    try:
        proxies = {
            "http":  f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        r = requests.get("https://www.google.com", proxies=proxies, timeout=5)
        return r.status_code == 200
    except:
        return False

# ─── Pick first working proxy ─────────────────────────────────────────────────
def pick_proxy():
    if not os.path.exists(PROXIES_FILE):
        return None

    with open(PROXIES_FILE) as f:
        candidates = [line.strip() for line in f if line.strip()]

    random.shuffle(candidates)
    for proxy in candidates:
        if is_proxy_working(proxy):
            return proxy
    return None

# ─── Bet365 scraper ───────────────────────────────────────────────────────────
async def scrape_bet365_nba_moneyline():
    proxy = pick_proxy()
    launch_args = {"headless": HEADLESS}
    if proxy:
        launch_args["proxy"] = {"server": f"http://{proxy}"}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_args)
        page    = await browser.new_page()
        await page.goto(
            "https://www.az.bet365.com/?_h=hcqvfaL5kFJPXQqyVxYhOg%3D%3D&btsffd=1#/AC/B18/C20604387/D48/E1453/F10"
            wait_until="networkidle"
        )
        await page.wait_for_selector(".ovm-FixtureDetailsTwoWay_TeamName", timeout=30000)
        await asyncio.sleep(2)

        games = await page.locator(".ovm-FixtureDetailsTwoWay").all()
        out   = []

        for g in games:
            teams = await g.locator(".ovm-FixtureDetailsTwoWay_TeamName").all_text_contents()
            odds  = await g.locator(".ovm-ParticipantOddsOnly_Odds").all_text_contents()
            if len(teams) == 2 and len(odds) == 2:
                t1, t2 = teams[0].strip(), teams[1].strip()
                o1, o2 = odds[0].strip(), odds[1].strip()
                out.append({
                    "team1": t1,
                    "team2": t2,
                    "odds": { t1: o1, t2: o2 }
                })

        await browser.close()
        return out

# ─── PointsBet scraper ────────────────────────────────────────────────────────
async def scrape_pointsbet_nba_moneyline():
    proxy = pick_proxy()
    launch_args = {"headless": HEADLESS}
    if proxy:
        launch_args["proxy"] = {"server": f"http://{proxy}"}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_args)
        page    = await browser.new_page()
        await page.goto("https://pointsbet.com.au/sports/basketball/NBA", wait_until="networkidle")
        await page.wait_for_selector(".f1fe3y5x", timeout=20000)
        await asyncio.sleep(2)

        blocks = await page.locator("a.f1rtv67w").all()
        out    = []

        for b in blocks:
            teams = await b.locator(".f1fe3y5x").all_text_contents()
            odds  = await b.locator(".fheif50").all_text_contents()
            if len(teams) >= 2 and len(odds) >= 2:
                t1, t2 = teams[0].strip(), teams[1].strip()
                o1, o2 = odds[0].strip(), odds[1].strip()
                out.append({
                    "team1": t1,
                    "team2": t2,
                    "odds": { t1: o1, t2: o2 }
                })

        await browser.close()
        return out

# ─── Entry point ──────────────────────────────────────────────────────────────
async def main():
    bet365_data = await scrape_bet365_nba_moneyline()
    points_data = await scrape_pointsbet_nba_moneyline()

    if PRINT_ODDS:
        print("Bet365 NBA moneylines:")
        print(json.dumps(bet365_data, indent=2))

        print("\nPointsBet NBA moneylines:")
        print(json.dumps(points_data, indent=2))

    # Also return the data if someone wants to import this module:
    return {
        "bet365": bet365_data,
        "pointsbet": points_data
    }

if __name__ == "__main__":
    asyncio.run(main())
