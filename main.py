import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from urllib.parse import urljoin
import json
import time

# Change the following variables to your requirements
START_URL = "https://python.langchain.com/v0.2/docs/tutorials/"
MAX_DEPTH = 2
OUTPUT_FILE = "scraped_data.json"

ua = UserAgent()

def get_new_tor_session():
    session = requests.session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    return session

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='your_password')  # Set your password here
        controller.signal(Signal.NEWNYM)
        time.sleep(5)  # Wait for new IP to be ready

def fetch_page(url, session):
    headers = {'User-Agent': ua.random}
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def scrape(url, session, depth, max_depth):
    if depth > max_depth:
        return

    page_content = fetch_page(url, session)
    if not page_content:
        return

    soup = BeautifulSoup(page_content, 'html.parser')
    data = {
        'url': url,
        'content': soup.get_text()
    }
    scraped_data.append(data)

    links = soup.find_all('a', href=True)
    for link in links:
        link_url = link['href']
        if link_url.startswith('/'):
            link_url = urljoin(url, link_url)
        if link_url.startswith(START_URL):
            scrape(link_url, session, depth + 1, max_depth)

scraped_data = []
session = get_new_tor_session()
scrape(START_URL, session, 0, MAX_DEPTH)

with open(OUTPUT_FILE, 'w') as f:
    json.dump(scraped_data, f, indent=4)

print(f"Scraping complete. Data saved to {OUTPUT_FILE}.")
