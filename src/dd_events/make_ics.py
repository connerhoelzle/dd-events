# the point is to take the raw json events data and convert it to ics format

import json
from icalendar import Calendar, Event
import datetime as dt
import zoneinfo
from pathlib import Path
import html
from bs4 import BeautifulSoup


def clean_description(raw_description_value):                               # cleans messy description value
    description = html.unescape(raw_description_value)                      # removes weird html stuff
    soup = BeautifulSoup(description, "html.parser")                        # creates soup object
    read_more = soup.find("a", class_="excerpt-read-more")                  # finds weird <a> class with "read more" text
    if read_more:
        read_more.decompose()                                               # executes if True
    description = soup.get_text(" ", strip=True).strip().replace("\\n", "") # inserts " " between fragments, replaces "\\n"
    return description


def get_event_info(raw_event_dict):                                                     # returns formatted event from raw event text
    start = dt.datetime.fromisoformat(raw_event_dict["startDate"]).astimezone(dt.timezone.utc)  # gets "startDate" value -> UTC
    end = dt.datetime.fromisoformat(raw_event_dict["endDate"]).astimezone(dt.timezone.utc)      # ""
    if end - start >= dt.timedelta(hours=24):
        start = start.date()
        end = end.date() + dt.timedelta(days=1)
    summary = raw_event_dict["name"]                                                            # gets "name" value
    description = raw_event_dict["description"]                                                 # gets "description" value
    component = Event.new(                                          # creates new event
                    start=start,                                    # inputs converted "startDate" value
                    end=end,                                        # ""
                    summary=html.unescape(summary),                 # "" after removing weird html stuff
                    description=clean_description(description)      # inputs cleaned "description" value
                    )
    return component





def main():
#import json data
    with open("dd_events.json", "r", encoding="utf-8") as file:  # with open() as : is a convention ensuring the file closes after run
        data = json.load(file)  # data is a list of dicts (list[0] is a dictionary created from json data)

    cal = Calendar.new(name="Downtown Dallas Events Calendar")      # defines calendar

    for raw_event in data:                          # iterates through data
        event_component = get_event_info(raw_event)           # gets formatted event info
        cal.add_component(event_component)                    # adds event info to calendar

    path = Path("dd_events.ics")
    path.write_bytes(cal.to_ical()) # using pathlib.Path is a more modern convention for working with filepaths vs. with open
