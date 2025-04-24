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

def setUp():
    # load setup configurations
    with open('setup.json', 'r') as fp:
        data = json.load(fp)
    driver_path = data["chromedriver_location"]
    options = Options()
    if data["headless"] == '1':
        options.add_argument('--headless')
    # set up proxy
    if os.path.exists('http_proxies.txt'):
        with open('http_proxies.txt', 'r') as file:
            proxies = file.readlines()
            if proxies:
                rand_proxy = random.choice(proxies).strip()
                options.add_argument(f'--proxy-server={rand_proxy}')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

#bet365
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

# Example usage
if __name__ == "__main__":
    nba_moneyline_odds = scrape_bet365_nba_moneyline()
    for game in nba_moneyline_odds:
        print(f"{game['team1']} vs {game['team2']}")
        print(f"Odds: {game['odds']}")
        print("-" * 30)
