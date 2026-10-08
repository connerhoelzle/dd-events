from bs4 import BeautifulSoup
import httpx
import pprint as pp

URL = 'https://www.uptowndallas.net/events'

def get_data(url):
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_events = []

    for item in soup.find_all('div', class_='u-hflex-left-top'):
        raw_events.append(item.parent)
    return raw_events

def main():
    raw_events = get_data(URL)
    events_list = []
    for event in raw_events:
        title = event.find('h3').text
        month = event.find('div', class_='u-text-sm').text
        date = event.find('div', class_='u-text-4xl').text
        time_address = []
        for child in event.find('div', class_='u-hflex-wrap').children:
            time_address.append(child.text)
        description = event.find('div', attrs={'m-event-card-content':''}).find('div').find_all('p', class_='u-leading-1-6')[-1].text
        event_dict = {'title': title, 'date': f'{month} {date}', 'time': time_address[0], 'address': time_address[2], 'description': description}
        events_list.append(event_dict)
    pp.pprint(events_list)
