# Required packages:
# pip install beautifulsoup4 ics playwright
# playwright install

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os

BASE_URL = 'https://www.visitlaramie.org'

def scrape_events(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)  # Wait 5 seconds for JS to load
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    events = []
    event_cards = soup.find_all('div', attrs={'data-type': 'events'})

    for card in event_cards:
        title_tag = card.select_one('div.info h4 a.title')
        title = title_tag.get_text(strip=True) if title_tag else 'No Title'
        link = BASE_URL + title_tag['href'] if title_tag and title_tag.has_attr('href') else ''

        month_tag = card.select_one('span.mini-date-container span.month')
        day_tag = card.select_one('span.mini-date-container span.day')

        event_date = None
        if month_tag and day_tag:
            try:
                month = month_tag.get_text(strip=True)
                day = day_tag.get_text(strip=True)
                year = datetime.now().year
                event_date = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            except ValueError:
                pass

        description = f"{title}\nMore info: {link}"
        location_tag = card.select_one('li.locations')
        location = location_tag.get_text(strip=True) if location_tag else ''

        events.append({
            'title': title,
            'date': event_date,
            'description': description,
            'location': location
        })

    return events

def create_ical(events, output_file='./docs/events.ics'):
    calendar = Calendar()

    for ev in events:
        if ev['date']:
            event = Event()
            event.name = ev['title']
            event.begin = ev['date'].strftime('%Y-%m-%d')
            event.description = ev['description']
            if ev['location']:
                event.location = ev['location']
            calendar.events.add(event)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.writelines(calendar)

if __name__ == "__main__":
    url = 'https://www.visitlaramie.org/events/'
    events = scrape_events(url)
    create_ical(events)
    print(f"Created events.ics with {len(events)} events!")
