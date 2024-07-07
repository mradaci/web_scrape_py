import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sqlite3
import time
import json
import logging
from html2image import Html2Image


# We are gonna use SQLite for the basic example here... but you can really use whatever you want, something in da cloud maybe. 

# Set up logging
logging.basicConfig(level=logging.INFO)

# SQLite setup
conn = sqlite3.connect('web_scraper.db')
c = conn.cursor()

# Create tables if they do not exist (This will be removed after first run, but this is meant to get someone started)
def create_tables():
    c.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        timestamp TEXT,
        html TEXT,
        data TEXT,
        screenshot BLOB
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER,
        media_type TEXT,
        media_url TEXT,
        media_data BLOB,
        FOREIGN KEY(page_id) REFERENCES pages(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        timestamp TEXT,
        error_message TEXT
    )
    ''')
    conn.commit()

# We need to knoe the errors, yo! Hoewever, I am not sure we need to log these to the DB. 
def log_error(url, error_message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO error_logs (url, timestamp, error_message) VALUES (?, ?, ?)',
              (url, timestamp, error_message))
    conn.commit()


visited_urls = set()

# Kinda self explanitory, no?
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        error_message = f"Failed to download image {url}: {e}"
        logging.error(error_message)
        log_error(url, error_message)
    return None

# Same
def get_screenshot(url):
    try:
        hti = Html2Image()
        screenshot_path = hti.screenshot(url=url, save_as='screenshot.png')
        with open(screenshot_path[0], 'rb') as f:
            screenshot = f.read()
        return screenshot
    except Exception as e:
        error_message = f"Failed to take screenshot of {url}: {e}"
        logging.error(error_message)
        log_error(url, error_message)
        return None

# Prob wanna rethink what we're storing here as the DB will become too large, too quick. 
def store_data(url, html, data, media_urls, screenshot):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO pages (url, timestamp, html, data, screenshot) VALUES (?, ?, ?, ?, ?)',
              (url, timestamp, html, json.dumps(data), screenshot))
    page_id = c.lastrowid
    for media_url in media_urls:
        media_data = download_image(
            media_url['url']) if media_url['type'] == 'image' else None
        c.execute('INSERT INTO media (page_id, media_type, media_url, media_data) VALUES (?, ?, ?, ?)',
                  (page_id, media_url['type'], media_url['url'], media_data))
    conn.commit()

# Review this if you want to change how the script navigates the urls, specifically at the recursive call section
def scrape(url):
    if url in visited_urls:
        return
    visited_urls.add(url)

    logging.info(f'Scraping {url}')
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        error_message = f"Failed to fetch {url}: {e}"
        logging.error(error_message)
        log_error(url, error_message)
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract data
    data = {
        'text': soup.get_text(),
        'links': [a['href'] for a in soup.find_all('a', href=True)],
        'images': [img['src'] for img in soup.find_all('img', src=True)],
        'videos': [video['src'] for video in soup.find_all('video', src=True)]
    }

    media_urls = [{'type': 'image', 'url': urljoin(
        url, src)} for src in data['images']]
    media_urls += [{'type': 'video',
                    'url': urljoin(url, src)} for src in data['videos']]

    screenshot = get_screenshot(url)

    store_data(url, response.text, data, media_urls, screenshot)

    # Recursively scrape links within the same domain
    domain = urlparse(url).netloc
    for link in data['links']:
        absolute_link = urljoin(url, link)
        if urlparse(absolute_link).netloc == domain:
            scrape(absolute_link)


def main(urls):
    create_tables()
    for url in urls:
        scrape(url)


if __name__ == '__main__':
    urls = ['https://www.shutterfly.com/']  # Replace with actual URLs you'll need scraped
    main(urls)
