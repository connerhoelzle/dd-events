# the point is to take the raw json events data and convert it to ics format

import json
from icalendar import Calendar, Event
import datetime as dt
import zoneinfo
import pprint
from pathlib import Path
import html
from bs4 import BeautifulSoup


#import json data
with open("dd_events.json", "r", encoding="utf-8") as file:  # with open() as : is a convention ensuring the file closes after run
    data = json.load(file)  # data is a list of dicts (list[0] is a dictionary created from json data)

# DEFINE ICS STRUCTURE. 
#test with minimum required data
#cal = Calendar.new()
#event = Event.new(
#                start=dt.datetime(2026, 3, 21, 6, 30, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
#                end=dt.datetime(2026, 3, 21, 7, 30, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
#                summary="meeting to develop the game the luncher")
#cal.add_component(event) # adds the above event to cal

#path = Path("test.ics")
#path.write_bytes(cal.to_ical()) # using pathlib.Path is a more modern convention for working with filepaths vs. with open

#go get necessary json data
# start = dt.datetime.fromisoformat(data[0]["startDate"]).astimezone(dt.timezone.utc)

# end = dt.datetime.fromisoformat(data[0]["endDate"]).astimezone(dt.timezone.utc)

# summary = data[0]["name"] 
cal = Calendar.new(name="Downtown Dallas Events Calendar")

for event in data:
    start = dt.datetime.fromisoformat(event["startDate"]).astimezone(dt.timezone.utc)
    end = dt.datetime.fromisoformat(event["endDate"]).astimezone(dt.timezone.utc)
    summary = event["name"] 
    description = event["description"]
    description=html.unescape(description)
    soup = BeautifulSoup(description, "html.parser")
    read_more = soup.find("a", class_="excerpt-read-more")
    if read_more:
        read_more.decompose()

    component = Event.new(
                    start=start,
                    end=end,
                    summary=html.unescape(summary),
                    description = soup.get_text(" ", strip=True).strip().replace("\\n", "")
                    )
    cal.add_component(component)


path = Path("dd_events.ics")
path.write_bytes(cal.to_ical()) # using pathlib.Path is a more modern convention for working with filepaths vs. with open


##format data as necessary



#input data into ics structure
# cal = Calendar.new(name="Downtown Dallas Events Calendar")
# event = Event.new(
#                start=start,
#                end=end,
#                summary=summary
#                )
# cal.add_component(event)
# print(cal.to_ical().decode())
# return formatted ics event
