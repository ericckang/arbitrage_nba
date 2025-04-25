from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import json
import os
import random
import time

def is_proxy_working(proxy):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        r = requests.get("https://www.google.com", proxies=proxies, timeout=5)
        return r.status_code == 200
    except:
        return False

def setUp():
    # load setup configurations
    with open('setup.json', 'r') as fp:
        data = json.load(fp)

    driver_path = data["chromedriver_location"]
    options = Options()

    if data["headless"] == '1':
        options.add_argument('--headless')

    if os.path.exists('http_proxies.txt'):
        with open('http_proxies.txt', 'r') as file:
            proxies = file.readlines()
            random.shuffle(proxies)
            for proxy in proxies:
                proxy = proxy.strip()
                if is_proxy_working(proxy):
                    options.add_argument(f'--proxy-server={proxy}')
                    break

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

#bet365 (They patched this :( )
def scrape_bet365_nba_moneyline():
    driver = setUp()
    try:
        # Navigate to Bet365 NBA section
        driver.get('https://www.az.bet365.com/?_h=hcqvfaL5kFJPXQqyVxYhOg%3D%3D&btsffd=1#/AC/B18/C20604387/D48/E1453/F10')
        wait = WebDriverWait(driver, 30)
        # Wait for the NBA games list to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ovm-FixtureDetailsTwoWay_TeamName')))
        time.sleep(5)  # Additional wait to ensure all elements load
        games = driver.find_elements(By.CLASS_NAME, 'ovm-FixtureDetailsTwoWay')
        nba_games = []
        for game in games:
            try:
                teams = game.find_elements(By.CLASS_NAME, 'ovm-FixtureDetailsTwoWay_TeamName')
                odds = game.find_elements(By.CLASS_NAME, 'ovm-ParticipantOddsOnly_Odds')
                if len(teams) == 2 and len(odds) == 2:
                    team1 = teams[0].text.strip()
                    team2 = teams[1].text.strip()
                    odd1 = odds[0].text.strip()
                    odd2 = odds[1].text.strip()
                    nba_games.append({
                        'team1': team1,
                        'team2': team2,
                        'odds': {
                            team1: odd1,
                            team2: odd2
                        }
                    })
            except Exception as e:
                print(f"Error parsing game: {e}")
        return nba_games
    except Exception as e:
        print(f"Error loading Bet365 NBA section: {e}")
        return []
    finally:
        driver.quit()

# Pointsbet
def scrape_pointsbet_nba_moneyline():
    driver = setUp()
    try:
        url = "https://pointsbet.com.au/sports/basketball/NBA"
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        # Wait for NBA "Events" section to load
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "NBA")]')))
        time.sleep(5)  # Allow odds and games to fully render

        games = driver.find_elements(By.CSS_SELECTOR, 'div[class*="EventCard"]')
        nba_games = []

        for game in games:
            try:
                teams = game.find_elements(By.CSS_SELECTOR, 'div[class*="EventParticipant_name"]')
                odds = game.find_elements(By.CSS_SELECTOR, 'div[class*="PriceButton_price"]')

                if len(teams) == 2 and len(odds) >= 2:
                    team1 = teams[0].text.strip()
                    team2 = teams[1].text.strip()
                    odd1 = odds[0].text.strip()
                    odd2 = odds[1].text.strip()
                    nba_games.append({
                        'team1': team1,
                        'team2': team2,
                        'odds': {
                            team1: odd1,
                            team2: odd2
                        }
                    })
            except Exception as e:
                print(f"Error parsing game: {e}")
        return nba_games
    except Exception as e:
        print(f"Error loading PointsBet NBA section: {e}")
        return []
    finally:
        driver.quit()

#Constantly scrape live game
def continuously_scrape_pointsbet(interval=10):
    while True:
        try:
            nba_games = scrape_pointsbet_nba_moneyline()
            os.system('clear')  # or 'cls' on Windows to clear terminal
            print(f"--- Live NBA Odds (Updated Every {interval}s) ---\n")
            if not nba_games:
                print("No live NBA games found.")
            else:
                for game in nba_games:
                    print(f"{game['team1']} vs {game['team2']}")
                    print(f"{game['team1']} odds: {game['odds'][game['team1']]}")
                    print(f"{game['team2']} odds: {game['odds'][game['team2']]}")
                    print("-" * 40)
        except Exception as e:
            print(f"Error during scrape: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    continuously_scrape_pointsbet(interval=10)  # update every 10 seconds

