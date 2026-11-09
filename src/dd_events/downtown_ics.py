import datetime as dt
import html
import json
from pathlib import Path

from bs4 import BeautifulSoup
from icalendar import Calendar, Event


# cleans messy description value
def clean_description(raw_description_value):                               
    description = html.unescape(raw_description_value)  # removes weird html stuff
    soup = BeautifulSoup(description, "html.parser")                        
    read_more = soup.find("a", class_="excerpt-read-more")  # finds weird <a> class with "read more" text
    if read_more:
        read_more.decompose()                                               
    description = soup.get_text(" ", strip=True).strip().replace("\\n", "") 
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
            return full_address, name 
        else:
            return None, name 


def get_event_info(raw_event_dict): # returns formatted event from raw event text
    start_iso_parse = dt.datetime.fromisoformat(raw_event_dict["startDate"])
    start = start_iso_parse.astimezone(dt.timezone.utc)  
    end_iso_parse = dt.datetime.fromisoformat(raw_event_dict["endDate"])
    end = end_iso_parse.astimezone(dt.timezone.utc)      
    if end - start >= dt.timedelta(hours=24):
        start = start.date()
        end = end.date() + dt.timedelta(days=1)
    summary = raw_event_dict["name"]                                                            
    description = raw_event_dict["description"]                                                 
    url = raw_event_dict["url"]
    street_address, name = get_postal_address(raw_event_dict.get("location")) 
    geo = get_geo(raw_event_dict.get("location"))
    component = Event.new(                                          
                    start=start,                                    
                    end=end,
                    summary=html.unescape(summary),
                    description=clean_description(description),
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
        apple_value = f"geo:{latitude},{longitude}"
        component.add(apple_property_name, apple_value) # formats apple-specific location data
    if street_address is not None:
        component.add("LOCATION", street_address) 
    return component





def main():
    path = 'data/raw/dd_events.json'
 
 # with open() as : is a convention ensuring the file closes after run
    with open(path, "r", encoding="utf-8") as file:  
        data = json.load(file)  
    cal = Calendar.new(name="Downtown Dallas Events Calendar")

    for raw_event in data:
        event_component = get_event_info(raw_event)
        cal.add_component(event_component)
    

    path = Path("docs/dd_events.ics")
    path.write_bytes(cal.to_ical())
