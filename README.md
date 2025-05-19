# Arbitrage Betting

A toolkit for scraping NBA money-line odds from Bet365 and PointsBet, with support for rotating proxies (Oxylabs or manual lists) and optional GPT-4 Vision parsing.

## Features

- Fetch rotating Oxylabs residential proxies  
- Clean & test manual proxy lists  
- Selenium-based scraper (`selenium/setup.py`)  
- Playwright-based scraper (`vision_playwright.py`)  
- GPT-4 Vision parser (`vision_scraper.py`)

## Prerequisites

- Python 3.8+  
- `pip install playwright selenium requests openai`  
- `playwright install`  

## Configuration

1. **API & credentials**  
   - Create `config.py` (in `.gitignore`) with:  
     ```python
     OPENAI_API_KEY   = "your-openai-key"
     OXYLABS_USERNAME = "customer-XXX"
     OXYLABS_PASSWORD = "YYY"
     PROXIES_ENDPOINT = "pr.oxylabs.io:7777"
     ```
2. **Settings**  
   - Edit `setup.json` for headless mode and printing flags:  
     ```json
     {
       "chromedriver_location": "/path/to/chromedriver",
       "headless": "1",
       "print_odds": "1"
     }
     ```

## Project Layout
Arbitrage Betting/
├─ calculations.py
├─ fetch_oxylabs_proxies.py # generate Oxylabs proxies → http_proxies.txt
├─ http_proxies.txt # tested proxy list
├─ main.py # (your entrypoint)
├─ manual_proxy_finding/
│ ├─ clean_proxies.py # filter “+” and Google-tested proxies
│ └─ proxy-list-raw.txt # raw proxy dumps
├─ selenium/
│ ├─ setup.json
│ └─ setup.py # Selenium NBA scraper
├─ vision_playwright.py # Playwright + Vision pipeline
└─ vision_scraper.py # local-image → GPT-4 Vision parser


## Usage

### 1. Fetch Oxylabs proxies  
```bash
python fetch_oxylabs_proxies.py
# writes working proxies to http_proxies.txt
python vision_playwright.py
