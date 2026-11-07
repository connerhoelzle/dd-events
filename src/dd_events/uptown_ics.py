# formats uptown json data into ics format
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event
import json

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
    ut_json_filepath = 'data/raw/ut_events.json'

    with open(ut_json_filepath, 'r', encoding='utf-8') as file:
        events_list = json.load(file)

    cal = Calendar.new(name="Uptown Dallas Event Calendar")

    for raw_event in events_list:
        edate = raw_event['date']
        etime = raw_event['time']
        start, end = to_dto(edate, etime)
        event = Event.new(
            summary=event['title'],
            start=start,
            end=end,
            location=event['address'],
            description=event['description']
            )
        cal.add_component(event)


    path = Path('docs/ut_events.ics')
    path.write_bytes(cal.to_ical())
