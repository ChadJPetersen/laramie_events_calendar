import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os

def scrape_events(url):
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []

    # Adjust these selectors based on page structure
    event_cards = soup.select('div.card')

    for card in event_cards:
        title = card.select_one('h3').get_text(strip=True) if card.select_one('h3') else 'No Title'
        date_text = card.select_one('.date').get_text(strip=True) if card.select_one('.date') else None
        description = card.select_one('p').get_text(strip=True) if card.select_one('p') else 'No Description'

        event_date = None
        if date_text:
            try:
                event_date = datetime.strptime(date_text, '%B %d, %Y')
            except ValueError:
                pass

        events.append({
            'title': title,
            'date': event_date,
            'description': description
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
            calendar.events.add(event)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.writelines(calendar)

if __name__ == "__main__":
    url = 'https://www.visitlaramie.org/events/'
    events = scrape_events(url)
    create_ical(events)
    print(f"Created events.ics with {len(events)} events!")
