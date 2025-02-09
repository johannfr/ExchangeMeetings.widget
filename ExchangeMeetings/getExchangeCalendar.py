#!/usr/bin/env python3

from icecream import ic
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


def get_config(filename):
    with open(filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


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

    start = EWSDateTime(today.year, today.month, today.day).replace(
        tzinfo=a.default_timezone  # Shouldn't this be "tz"?
    )
    end = EWSDateTime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59).replace(
        tzinfo=a.default_timezone  # Shouldn't this be "tz"?
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
    meetings = main(days_to_fetch, filename=filename_config)
    with open(filename_data, "w") as text_file:
        json.dump({"meetings": meetings}, text_file, indent=4)
