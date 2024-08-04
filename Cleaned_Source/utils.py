import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def scrape_urls(url, depth, max_depth, start_url):
    if depth > max_depth:
        return []

    page_content = fetch_page(url)
    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
    links = soup.find_all('a', href=True)
    urls = [urljoin(url, link['href']) for link in links if link['href'].startswith('/')]

    all_urls = []
    for link_url in urls:
        if link_url.startswith(start_url):
            all_urls.append(link_url)
            all_urls.extend(scrape_urls(link_url, depth + 1, max_depth, start_url))

    return all_urls
