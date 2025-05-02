# Required packages:
# pip install --user -r requirements.txt

import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone
import json
import os
import time
import random
from functools import wraps
from dateutil import parser, tz

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.visitlaramie.org/events/',
}
mountainTimeZone = tz.gettz('America/Denver')

def retry(max_attempts=2, delay=3, retry_exceptions=(requests.RequestException,), backoff=2, jitter=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not isinstance(e, retry_exceptions):
                        raise
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = current_delay + random.uniform(0, jitter)
                        print(f"Attempt {attempt + 1} failed with {e}. Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        current_delay *= backoff
                    else:
                        raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=2, delay=3)
def fetch_simple_token():
    response = requests.get("https://www.visitlaramie.org/plugins/core/get_simple_token/", headers=HEADERS)
    response.raise_for_status()
    return response.text.strip().strip('"')

def fetch_categories():
    page_url = 'https://www.visitlaramie.org/events/'
    response = requests.get(page_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    categories = []

    for script_tag in soup.find_all('script'):
        script_content = script_tag.text

        if 'categories = [' in script_content:
            start_index = script_content.find('categories = [') + len('categories = ')
            end_index = script_content.find('];', start_index) + 1
            categories_json = script_content[start_index:end_index]
            category_data = json.loads(categories_json)
            categories = [item['value'] for item in category_data]

    if not categories:
        raise ValueError("Categories not found!")

    return categories

@retry(max_attempts=2, delay=3)
def fetch_events(params):
    response = requests.get('https://www.visitlaramie.org/includes/rest_v2/plugins_events_events_by_date/find', params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def scrape_events():
    categories = fetch_categories()
    token = fetch_simple_token()
    # Set start and end dates for the date_range at midnight Mountain Time
    now_mt = datetime.now(mountainTimeZone)
    start_mt = now_mt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_mt = (start_mt + timedelta(days=30))
    # Convert to UTC for the API
    start_date = start_mt.astimezone(timezone.utc)
    future_utc = end_mt.astimezone(timezone.utc)

    json_query = {
        "filter": {
            "active": True,
            "$and": [
                {
                    "categories.catId": {
                        "$in": categories
                    }
                }
            ],
            "date_range": {
                "start": {
                    "$date": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                },
                "end": {
                    "$date": future_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                }
            }
        },
        "options": {
            "limit": 100,
            "skip": 0,
            "count": True,
            "castDocs": False,
            "fields": {
                "_id": 1,
                "location": 1,
                "date": 1,
                "startDate": 1,
                "endDate": 1,
                "recurrence": 1,
                "recurType": 1,
                "latitude": 1,
                "longitude": 1,
                "media_raw": 1,
                "recid": 1,
                "title": 1,
                "url": 1,
                "categories": 1,
                "listing.primary_category": 1,
                "listing.title": 1,
                "listing.url": 1
            },
            "hooks": [],
            "sort": {
                "date": 1,
                "rank": 1,
                "title_sort": 1
            }
        }
    }
    
    data = fetch_events({
        "json": json.dumps(json_query),
        "token": token
    })
    items = data.get('docs', {}).get('docs', [])

    events = []
    for item in items:
        title = item.get('title', 'No Title').strip().replace('\n', ' ')
        start_date_str = item.get('startDate')
        event_date = None
        if start_date_str:
            try:
                event_date = parser.isoparse(start_date_str)
            except ValueError:
                pass
        end_date_str = item.get('endDate')
        end_date = None
        if end_date_str:
            try:
                end_date = parser.isoparse(end_date_str)
            except ValueError:
                pass

        # Use location as a string
        location = item.get('location', '').strip().replace('\n', ' ')
        link = item.get('url', '')
        # Extract category names
        categories = [cat.get('catName', '') for cat in item.get('categories', [])]
        categories_str = ', '.join(categories)
        # Extract media url if present
        media_url = ''
        media = item.get('media_raw', [])
        if media and isinstance(media, list):
            media_url = media[0].get('mediaurl', '')
        # Extract venue info if present
        listing = item.get('listing', {})
        venue = listing.get('title', '')
        venue_url = listing.get('url', '')

        # Build a description
        description = title
        if link:
            description += f"\nMore info: https://www.visitlaramie.org{link}"
        if venue:
            description += f"\nVenue: {venue}"
        if venue_url:
            description += f"\nVenue Info: https://www.visitlaramie.org{venue_url}"
        if media_url:
            description += f"\nImage: {media_url}"
        if categories_str:
            description += f"\nCategories: {categories_str}"
        
        events.append({
            'title': title,
            'date': event_date,
            'endDate': end_date,
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
            dt = ev['date']
            is_all_day = False
            # Check if time is midnight Mountain Time
            dt_mt = dt.astimezone(mountainTimeZone)
            if dt_mt.hour == 0 and dt_mt.minute == 0 and dt_mt.second == 0:
                is_all_day = True
            if is_all_day:
                event.begin = dt.date()
                event.make_all_day()
            else:
                event.begin = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                # Set end time if it exists
                if 'endDate' in ev and ev['endDate']:
                    end_dt = ev['endDate']
                    event.end = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            event.description = ev['description']
            if ev['location']:
                event.location = ev['location']
            calendar.events.add(event)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.writelines(calendar)

if __name__ == "__main__":
    events = scrape_events()
    create_ical(events)
    print(f"Created events.ics with {len(events)} events!")
