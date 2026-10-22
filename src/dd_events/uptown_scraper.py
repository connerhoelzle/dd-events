import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

# checks for two classes necessary to signify calendar graphic
def find_cal_graphic(class_list):
    if class_list is None:
        return False
    return 'u-relative' in class_list and 'u-sm-mb-4' in class_list


def get_data(url):
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    raw_events = []
# find cal, then find parent class    
    for item in soup.find_all('div', class_=find_cal_graphic):
        item = item.parent
        raw_events.append(item)
    return raw_events

def to_dto(date, time):
    today = dt.datetime.today()
    this_year = dt.datetime.today().year
    next_year = this_year + 1
    ninety_days = dt.timedelta(days=90)

    dtodate = (dt.datetime.strptime(date, '%b %d')
                .replace(year=this_year))

    if (today - dtodate) > ninety_days:
        dtodate = dtodate.replace(year=next_year)

    if time != '':
        dtotime = dt.datetime.strptime(time, '%I:%M%p').time()
        start_dto = dt.datetime.combine(dtodate, dtotime)
        start_dto = start_dto.replace(tzinfo=ZoneInfo('America/Chicago'))
        end_dto = start_dto + dt.timedelta(hours=3)
    else:
        start_dto = dtodate.date()
        end_dto = start_dto + dt.timedelta(days=1)
    return start_dto, end_dto



def main():
    URL = 'https://www.uptowndallas.net/events'
    raw_events = get_data(URL)
    events_list = []
    for event in raw_events:
        title = event.find('h3').text
        month = event.find('div', class_='u-text-sm').text
        date = event.find('div', class_='u-text-4xl').text

        time_address = []
        for child in event.find('div', class_='u-hflex-wrap').children:
            time_address.append(child.text)
        description = (
            event.find('div', attrs={'m-event-card-content':''})
            .find('div')
            .find_all('p', class_='u-leading-1-6')[-1]
            .text
            )
        event_dict = {'title': title.strip(),
                      'date': f'{month} {date}',
                      'time': time_address[0],
                      'address': time_address[2],
                      'description': description
                      }

        events_list.append(event_dict)
    cal = Calendar.new(name="Uptown Dallas Event Calendar")
    
    for scraped_event in events_list:
        edate = scraped_event['date']
        etime = scraped_event['time']
        start, end = to_dto(edate, etime)
        event = Event.new(
            summary=scraped_event['title'],
            start=start,
            end=end,
            location=scraped_event['address'],
            description=scraped_event['description']
            )
        cal.add_component(event)

    path = Path('docs/ut_events.ics')
    path.write_bytes(cal.to_ical())
