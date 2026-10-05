# the point is to take the raw json events data and convert it to ics format

import datetime as dt
import html
import json
from pathlib import Path

from bs4 import BeautifulSoup
from icalendar import Calendar, Event


def clean_description(raw_description_value):                               # cleans messy description value
    description = html.unescape(raw_description_value)                      # removes weird html stuff
    soup = BeautifulSoup(description, "html.parser")                        # creates soup object
    read_more = soup.find("a", class_="excerpt-read-more")                  # finds weird <a> class with "read more" text
    if read_more:
        read_more.decompose()                                               # executes if True
    description = soup.get_text(" ", strip=True).strip().replace("\\n", "") # inserts " " between fragments, replaces "\\n"
    return description

def get_geo(raw_location_dict):
    if raw_location_dict is None:
        return None
    if raw_location_dict.get("geo") is None:
        return None
    latitude = raw_location_dict.get("geo").get("latitude")
    longitude = raw_location_dict.get("geo").get("longitude")
    if (latitude is not None) and (longitude is not None):
        geo_coordinates = (float(latitude), float(longitude))
        return geo_coordinates
    else:
        return None

def get_postal_address(raw_location_dict):
    if raw_location_dict is None:
        return None, None
    if raw_location_dict.get("name") is None:
        name = None
    else: 
        name = raw_location_dict.get("name")

    get_address = raw_location_dict.get("address")
    if get_address is not None:
        street_address = get_address.get("streetAddress")
        address_locality = get_address.get("addressLocality")
        address_region = "Texas"
        postal_code = get_address.get("postalCode")
        country = "United States"
        if (
            street_address is not None
            and address_locality is not None
            and postal_code is not None
            ):

            full_address = (
                    f"{name}\n{street_address}\n{address_locality}, "
                    f"{address_region} {postal_code}\n{country}"
                    )
            return full_address, name # returns tuple so that I can work with name on the X-APPLE line
        else:
            return None, name # returns tuple so that the street_address, name = line works whether there is location data or not
    else:
        return None, name


def get_event_info(raw_event_dict):                                                     # returns formatted event from raw event text
    start_iso_parse = dt.datetime.fromisoformat(raw_event_dict["startDate"])
    start = start_iso_parse.astimezone(dt.timezone.utc)  # gets "startDate" value -> UTC
    end_iso_parse = dt.datetime.fromisoformat(raw_event_dict["endDate"])
    end = end_iso_parse.astimezone(dt.timezone.utc)      # ""
    if end - start >= dt.timedelta(hours=24):
        start = start.date()
        end = end.date() + dt.timedelta(days=1)
    summary = raw_event_dict["name"]                                                            # gets "name" value
    description = raw_event_dict["description"]                                                 # gets "description" value
    url = raw_event_dict["url"]
    street_address, name = get_postal_address(raw_event_dict.get("location")) # tuple so that I can work with name in X-APPLE line
    geo = get_geo(raw_event_dict.get("location"))
    component = Event.new(                                          # creates new event
                    start=start,                                    # inputs converted "startDate" value
                    end=end,                                        # ""
                    summary=html.unescape(summary),                 # "" after removing weird html stuff
                    description=clean_description(description),      # inputs cleaned "description" value
                    url=url
                    )
    if geo != None: 
        component.add("GEO", geo)
        latitude = geo[0]
        longitude = geo[1]
        
        name = html.unescape(name)
        
        apple_property_name = ("X-APPLE-STRUCTURED-LOCATION;"
                               "VALUE=URI;X-TITLE="f"\"{name}\""
                               )
        apple_value = f"geo:{geo[0]},{geo[1]}"
        component.add(apple_property_name, apple_value) # formats apple-specific location data
    if street_address is not None:
        component.add("LOCATION", street_address) 
    return component





def main():
#import json data
    with open("dd_events.json", "r", encoding="utf-8") as file:  # with open() as : is a convention ensuring the file closes after run
        data = json.load(file)  # data is a list of dicts (list[0] is a dictionary created from json data)

    cal = Calendar.new(name="Downtown Dallas Events Calendar")      # defines calendar

    for raw_event in data:                          # iterates through data
        event_component = get_event_info(raw_event)           # gets formatted event info
        cal.add_component(event_component)                    # adds event info to calendar
    

    path = Path("docs/dd_events.ics")
    path.write_bytes(cal.to_ical()) # using pathlib.Path is a more modern convention for working with filepaths vs. with open
