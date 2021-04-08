#--------------------------------------------------------------------------------------
# Installation:
# This script uses a Python3 helper script to retrieve upcoming calendar items.
# Run the commands below from a command.  It runs python in an isolated environment.
#
# python3 -m venv ExchangeMeetings/venv
# source ExchangeMeetings/venv/bin/activate ; pip install --upgrade pip
# source ExchangeMeetings/venv/bin/activate ; pip install -r ExchangeMeetings/requirements.txt
#--------------------------------------------------------------------------------------
# Execute the shell command.
command: "source ExchangeMeetings/venv/bin/activate; python3 ExchangeMeetings/getExchangeCalendar.py"

# Set the refresh frequency (milliseconds).
refreshFrequency: 30000
# refreshFrequency: 1000

# Render the output.
render: (output) -> """
  <div id='meetings'></div>
"""

# Update the rendered output.
update: (output, domEl) ->
  dom = $(domEl)
  days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  dowfound = [0, 0, 0, 0, 0, 0, 0, 0]
  nextfound = false  # assumes json file is already sorted by start datetime
  tomorrowfound = false
  data = JSON.parse output
  html = '<p class="meetings">Today</p><ul>\n'
  cnt = 0
  limit = 8

  # Loop through  the meetings
  today = new Date
  dd = today

  for mtg in data.meetings.slice(0,limit+1)
    classes = []
    if cnt > limit
      html += "+ " + (data.meetings.length - cnt) + " more"
    else
      cnt += 1
      dt = new Date mtg.start
      dt_end = new Date mtg.end
      delta = dt - dd
      duration = (dt_end - dt)/60000
      dowdelta = dt.getDay() - today.getDay()
      dow_num = dt.getDay()
      dow_num_prev = dow_num - 1
      if dow_num_prev == -1
        dow_num_prev = 6
      dowfound[dow_num] += 1

      if dow_num - today.getDay() == 1 and not tomorrowfound
        if dowfound[dow_num_prev] == 0
          html += '<li class="meetings">None</li>'
        html += '</ul><p class="meetings">Tomorrow</p><ul>\n'
        tomorrowfound = true
      if dowdelta > 1 and dowfound[dow_num] <= 1
        if dowfound[dow_num_prev] == 0
          html += '<p class="meetings">None</p>'
        html += '</ul><p class="meetings">' + days[dt.getDay()] + "</p><ul>"
      if delta < 0
        classes.push "past"
      else
        if !nextfound
           classes.push "next"
           nextfound = true
        else
           classes.push "future"

      if mtg.cancelled
           classes.push "cancelled"
      if mtg.zoom.url != null
           classes.push "zoom"

      url = mtg.zoom.url

      html += "<li class='" + classes.join(" ") + "'>"
      if url != null
        html += "<a href='" + url += "'>"
      html += dt.toLocaleTimeString().replace /:[0-9]+$/, " " + " - "
      if mtg.subject.length > 35
        html += mtg.subject.substr(0,32) + "..."
      else
        html += mtg.subject

      if delta > 0
         # show time until on next meeting
         mins = Math.round(delta/60000)
         hours = Math.round(delta/360000)/10
         if hours >= 2.0
          html += " (in " + hours + " hrs)"
         else
           html += " (in " + mins + " min)"
      html += "<br>"
      # if your exchange server includes extra info such as userid or contract company in names, uncomment this to clean it up a bit
      # organizer = mtg.organizer.match(/([A-Za-z ]+)\s/ig)
      # html += organizer[0].replace /\s+$/g, "" + ', ' + duration + " mins, "
      html += "&nbsp;" + mtg.organizer + ', ' + duration + " mins, "
      if mtg.required_attendees.length > 0
        html += mtg.required_attendees.length + " required"
      if mtg.optional_attendees.length > 0
        html += " (" + mtg.optional_attendees.length + " optional)"
      if url != null
        html += '</a>'
      html += "</li>\n";


  # Set our output.
  $(meetings).html(html)

# CSS Style
style: """
  margin:0
  padding:4px
  left:10px
  top: 150px
  background:rgba(#fff, .15)
  border:1px solid rgba(#111, .10)
  border-radius:10px
  font-family: Arial
  font-size: 14px
  color: rgba(#eff, .20)
  a { color: white; text-decoration: none; }

  .meetings
    text-align:left
    color: rgba(#fff, 1.00)

  .past, .next, .future
    padding:2px
    margin:2px

  .past
    color: rgba(#fff, .20)
    text-decoration: line-through;
  a { color: rgba(#fff, .20); text-decoration: line-through; }

  .next_cancelled
    font-weight:bold
    color: rgba(#eff, 1.0)
    a { color: rgba(#fff, 1.0); text-decoration: line-through; }

  .next
    font-weight:bold
    color: rgba(#eff, 1.0)
    a { color: rgba(#fff, 1.0); text-decoration: none; }

  .future
    font-weight:regular
    color: rgba(#fff, .60)
    a { color: rgba(#fff, .60); text-decoration: none; }

  li.zoom
    list-style-image: url('ExchangeMeetings/icon_zoom.png')

"""
