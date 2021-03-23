# uebersicht-widget-Exchange

This is a fork of https://github.com/rtphokie/ExchangeMeetings.widget

ExchangeMeetings fetches upcoming meetings and appointments on your Exchange calendar and displays them in a brief [Übersicht](http://tracesof.net/uebersicht/) widget. 

![screenshot.png](screenshot.png?raw=true "ExchangeMeetings")

## Requirements
* [Python3](https://www.python.org/downloads/mac-osx/)

## Features
* Clickable shortcut ([in Übersicht preferences](http://tracesof.net/blog/2015/11/29/clickable-widgets-experiment/)) to join Zoom meetings
* Exchange calendar entries for today and tomorrow
* meeting subject, duration, duration, number of attendees (required and optional)
* Zoom meetings are identified with icons and are clickable to join
* past meetings are dimmed, next upcoming meeting is highlighted

## Installation
The virtual environment the Python3 script runs inside is easy to setup

Move/Copy the `ExchangeMeetings` subfolder to your widgets folder (e.g. `~/Library/Application\ Support/Übersicht/widgets`)

Open a terminal to that same widgets folder, and run the following commands to create the environment and install the required Python modules:

```
python3 -m venv ExchangeMeetings/venv
ExchangeMeetings/venv/bin/python -m pip install -r ExchangeMeetings/requirements.txt
```

Add your configuration to a file named ExchangeMeetings_config.yml in your widgets-folder (i.e. next to the `ExchangeEvents` folder):

```
email: your.address@domain.com
username: yaddress@domain.com
password: S4cr37
timezone: Europe/Copenhagen
ttl: 600
```

 * If your e-mail address and your login credentials is the same, you just put the same one in both fields.
 * The TTL time (how long to cache the results) is in seconds.
 * Since your password is stored in plain-text, you should probably make sure that other users can't read the configuration-file: `chmod go-rwx ExchangeMeetings_config.yml`
