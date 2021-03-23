#!/usr/bin/env python3

import json
import os
from pprint import pprint
from datetime import datetime, timedelta
import pytz
import re
import time
import yaml
from exchangelib import (
    Credentials,
    Account,
    EWSTimeZone,
    EWSDateTime,
)  # https://github.com/ecederstrand/exchangelib

days_to_fetch = 3
cache_time_to_live = (
    900  # cache exchange data for 15 minutes, configurable in yaml file
)
max_cache_age = 43200  # dont cache for more than 12 hours


def get_config(filename):
    with open(filename) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    cache_time_to_live = config["ttl"]
    return config


def main(days, filename="ExchangeMeetings/ExchangeMeetings_config.yml"):
    config = get_config(filename)
    data = fetch_from_exchange(days, config)
    return data


def fetch_from_exchange(days, config):
    now = datetime.now(tz=pytz.UTC)
    credentials = Credentials(config["username"], config["password"])
    a = Account(config["email"], credentials=credentials, autodiscover=True)
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    if tomorrow.weekday() >= 5:
        # ensure Monday is included Fri-Sun
        tomorrow = today + timedelta(days=8 - tomorrow.weekday())

    try:
        tz = a.default_timezone
    except:
        tz = EWSTimeZone.timezone(config["tz"])
    start = a.default_timezone.localize(EWSDateTime(today.year, today.month, today.day))
    end = a.default_timezone.localize(
        EWSDateTime(tomorrow.year, tomorrow.month, tomorrow.day)
    )
    items = a.calendar.view(start=start, end=end).only(
        "uid",
        "start",
        "end",
        "duration",
        "subject",
        "text_body",
        "my_response_type",
        "organizer",
        "importance",
        "is_cancelled",
        "is_all_day",
        "is_recurring",
        "location",
        "optional_attendees",
        "required_attendees",
    )
    results = []

    for item in items:
        duration = item.end - item.start
        optional = []
        required = []
        if item.optional_attendees:
            for optional_attendee in item.optional_attendees:
                optional.append(optional_attendee.mailbox.name)
        if item.required_attendees:
            for required_attendee in item.required_attendees:
                required.append(required_attendee.mailbox.name)

        # dt = new Date "February 19, 2016 23:15:00"
        datefmt = "%B %d, %Y %H:%M"
        try:
            start = item.start.astimezone(tz).strftime(datefmt)
            end = item.end.astimezone(tz).strftime(datefmt)
        except:
            start = item.start.strftime(datefmt)
            end = item.end.strftime(datefmt)
        result = {
            "start": start,
            "end": end,
            "subject": item.subject,
            "response": item.my_response_type,
            "recurring": item.is_recurring,
            "cancelled": item.is_cancelled,
            "uid": item.uid,
            "url": None,
            "url_type": None,
            "location": item.location,
            "duration_seconds": duration.seconds,
            "duration_min": int(duration.seconds / 20),
            "text_body": item.text_body,
            "organizer": item.organizer.name,
            "zoom": {
                "url": None,
            },
            "required_attendees": required,
            "optional_attendees": optional,
        }
        zoom_parse(item, result)
        results.append(result)

    return sorted(results, key=lambda i: (i["start"], i["end"]))


def zoom_parse(item, result):
    if type(item.text_body) is str:
        zoom_url_join = re.search(
            "\r\nJoin Zoom Meeting\r\n(.+)\r\n", item.text_body, re.IGNORECASE
        )
        if zoom_url_join:
            url = (
                zoom_url_join.group(1)
                .replace("https://", "zoommtg://")
                .replace("/j/", "/join?confno=")
                .replace("?pwd=", "&pwd=")
            )
            result["zoom"]["url"] = url
            result["url_type"] = "zoom"


if __name__ == "__main__":
    filename_data = "ExchangeMeetings/meetings.json"
    filename_config = "ExchangeMeetings/ExchangeMeetings_config.yml"
    filename_data = "meetings.json"
    filename_config = "ExchangeMeetings_config.yml"
    # cache_time_to_live = 1
    if os.path.isfile(filename_data):
        st = os.stat(filename_data)
        fileage = time.time() - st.st_mtime
    else:
        fileage = cache_time_to_live + 1
    if fileage > cache_time_to_live:
        try:
            meetings = main(days_to_fetch, filename=filename_config)
            with open(filename_data, "w") as text_file:
                json.dump({"meetings": meetings}, text_file, indent=4)
            pprint(meetings)
        except Exception as e:
            raise
            pass  # Exchange API is unreliable, fall back to cache
    if os.path.isfile(filename_data):
        with open(filename_data, "r") as text_file:
            print(text_file.read())
    else:
        print(json.dumps({"error": f"data file {filename_data} not found"}))
