#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Make actions for Marvin, one function for each action.
"""
from urllib.parse import quote_plus
from urllib.request import urlopen
import calendar
import datetime
import json
import random
import requests

from bs4 import BeautifulSoup


def getAllActions():
    """
    Return all actions in an array.
    """
    return [
        marvinExplainShell,
        marvinGoogle,
        marvinLunch,
        marvinVideoOfToday,
        marvinWhoIs,
        marvinHelp,
        marvinSource,
        marvinBudord,
        marvinQuote,
        marvinStats,
        marvinIrcLog,
        marvinListen,
        marvinWeather,
        marvinSun,
        marvinSayHi,
        marvinSmile,
        marvinStrip,
        marvinTimeToBBQ,
        marvinBirthday,
        marvinNameday,
        marvinUptime,
        marvinStream,
        marvinPrinciple,
        marvinJoke,
        marvinCommit
    ]


# Load all strings from file
with open("marvin_strings.json", encoding="utf-8") as f:
    STRINGS = json.load(f)

# Configuration loaded
CONFIG = None

def setConfig(config):
    """
    Keep reference to the loaded configuration.
    """
    global CONFIG
    CONFIG = config


def getString(key, key1=None):
    """
    Get a string from the string database.
    """
    data = STRINGS[key]
    if isinstance(data, list):
        res = data[random.randint(0, len(data) - 1)]
    elif isinstance(data, dict):
        if key1 is None:
            res = data
        else:
            res = data[key1]
            if isinstance(res, list):
                res = res[random.randint(0, len(res) - 1)]
    elif isinstance(data, str):
        res = data

    return res


def marvinSmile(row, asList=None, asStr=None):
    """
    Make Marvin smile.
    """
    msg = None
    if row.intersection(['smile', 'le', 'skratta', 'smilies']):
        smilie = getString("smile")
        msg = "{SMILE}".format(SMILE=smilie)
    return msg


def marvinGoogle(row, asList=None, asStr=None):
    """
    Let Marvin present an url to google.
    """
    msg = None
    match = row.intersection(['google', 'googla'])

    if match:
        # Find the google word and take the rest as the query string
        startAt = next(iter(match))
        searchStart = asList.index(startAt) + 1

        if searchStart >= len(asList):
            searchStr = ""
        else:
            searchStr = " ".join(asList[searchStart:])

        url = "https://www.google.se/search?q="
        url += quote_plus(searchStr)
        google = getString("google")
        msg = google.format(url)

    return msg


def marvinExplainShell(row, asList=None, asStr=None):
    """
    Let Marvin present an url to the service explin shell to
    explain a shell command.
    """
    msg = None
    match = row.intersection(['explain', 'förklara'])

    if match:
        # Find the matching word and take the rest as the query string
        matchedStr = match.pop()
        startAt = asStr.find(matchedStr) + len(matchedStr)
        searchStr = asStr[startAt:].strip()

        url = "http://explainshell.com/explain?cmd="
        url += quote_plus(searchStr, "/:")
        explain = getString("explainShell")
        msg = explain.format(url)

    return msg


def marvinSource(row, asList=None, asStr=None):
    """
    State message about sourcecode.
    """
    msg = None
    if row.intersection(['källkod', 'source']):
        msg = getString("source")

    return msg


def marvinBudord(row, asList=None, asStr=None):
    """
    What are the budord for Marvin?
    """
    msg = None
    if row.intersection(['budord', 'stentavla']):
        if row.intersection(['1', '#1']):
            msg = getString("budord", "#1")
        elif row.intersection(['2', '#2']):
            msg = getString("budord", "#2")
        elif row.intersection(['3', '#3']):
            msg = getString("budord", "#3")
        elif row.intersection(['4', '#4']):
            msg = getString("budord", "#4")
        elif row.intersection(['5', '#5']):
            msg = getString("budord", "#5")

    return msg


def marvinQuote(row, asList=None, asStr=None):
    """
    Make a quote.
    """
    msg = None
    if row.intersection(['quote', 'citat', 'filosofi', 'filosofera']):
        msg = getString("hitchhiker")

    return msg


def videoOfToday():
    """
    Check what day it is and provide a url to a suitable video together with a greeting.
    """
    dayNum = datetime.date.weekday(datetime.date.today()) + 1
    msg = getString("weekdays", str(dayNum))
    video = getString("video-of-today", str(dayNum))

    if video:
        msg += " En passande video är " + video
    else:
        msg += " Jag har ännu ingen passande video för denna dagen."

    return msg


def marvinVideoOfToday(row, asList=None, asStr=None):
    """
    Show the video of today.
    """
    msg = None
    if row.intersection(['idag', 'dagens']) and row.intersection(['video', 'youtube', 'tube']):
        msg = videoOfToday()

    return msg


def marvinWhoIs(row, asList=None, asStr=None):
    """
    Who is Marvin.
    """
    msg = None
    if row.issuperset(['vem', 'är']):
        msg = getString("whois")

    return msg


def marvinHelp(row, asList=None, asStr=None):
    """
    Provide a menu.
    """
    msg = None
    if row.intersection(['hjälp', 'help', 'menu', 'meny']):
        msg = getString("menu")

    return msg


def marvinStats(row, asList=None, asStr=None):
    """
    Provide a link to the stats.
    """
    msg = None
    if row.intersection(['stats', 'statistik', 'ircstats']):
        msg = getString("ircstats")

    return msg


def marvinIrcLog(row, asList=None, asStr=None):
    """
    Provide a link to the irclog
    """
    msg = None
    if row.intersection(['irc', 'irclog', 'log', 'irclogg', 'logg', 'historik']):
        msg = getString("irclog")

    return msg


def marvinSayHi(row, asList=None, asStr=None):
    """
    Say hi with a nice message.
    """
    msg = None
    if row.intersection([
            'snälla', 'hej', 'tjena', 'morsning', 'morrn', 'mår', 'hallå',
            'halloj', 'läget', 'snäll', 'duktig', 'träna', 'träning',
            'utbildning', 'tack', 'tacka', 'tackar', 'tacksam'
    ]):
        smile = getString("smile")
        hello = getString("hello")
        friendly = getString("friendly")
        msg = "{} {} {}".format(smile, hello, friendly)

    return msg


def marvinLunch(row, asList=None, asStr=None):
    """
    Help decide where to eat.
    """
    lunchOptions = {
        'stan centrum karlskrona kna': 'lunch-karlskrona',
        'ängelholm angelholm engelholm': 'lunch-angelholm',
        'hässleholm hassleholm': 'lunch-hassleholm',
        'malmö malmo malmoe': 'lunch-malmo',
        'göteborg gbg': 'lunch-goteborg'
    }

    if row.intersection(['lunch', 'mat', 'äta', 'luncha']):
        lunchStr = getString('lunch-message')

        for keys, value in lunchOptions.items():
            if row.intersection(keys.split(' ')):
                return lunchStr.format(getString(value))

        return lunchStr.format(getString('lunch-bth'))

    return None


def marvinListen(row, asList=None, asStr=None):
    """
    Return music last listened to.
    """
    msg = None

    if row.intersection(['lyssna', 'lyssnar', 'musik']):

        if not CONFIG["lastfm"]:
            return getString("listen", "disabled")

        url = "http://ws.audioscrobbler.com/2.0/"

        try:
            params = dict(
                method="user.getrecenttracks",
                user=CONFIG["lastfm"]["user"],
                api_key=CONFIG["lastfm"]["apikey"],
                format="json",
                limit="1"
            )

            resp = requests.get(url=url, params=params)
            data = json.loads(resp.text)

            artist = data["recenttracks"]["track"][0]["artist"]["#text"]
            title = data["recenttracks"]["track"][0]["name"]
            link = data["recenttracks"]["track"][0]["url"]

            msg = getString("listen", "success").format(artist=artist, title=title, link=link)

        except Exception:
            msg = getString("listen", "failed")

    return msg


def marvinSun(row, asList=None, asStr=None):
    """
    Check when the sun goes up and down.
    """
    msg = None
    if row.intersection(['sol', 'solen', 'solnedgång', 'soluppgång']):
        try:
            soup = BeautifulSoup(urlopen('http://www.timeanddate.com/sun/sweden/jonkoping'))
            spans = soup.find_all("span", {"class": "three"})
            sunrise = spans[0].text
            sunset = spans[1].text
            msg = getString("sun").format(sunrise, sunset)

        except Exception:
            msg = getString("sun-no")

    return msg


def marvinWeather(row, asList=None, asStr=None):
    """
    Check what the weather prognosis looks like.
    """
    msg = None
    if row.intersection(["väder", "vädret", "prognos", "prognosen", "smhi"]):
        url = getString("smhi", "url")
        try:
            soup = BeautifulSoup(urlopen(url))
            msg = "{}. {}. {}".format(
                soup.h1.text,
                soup.h4.text,
                soup.h4.findNextSibling("p").text
            )

        except Exception:
            msg = getString("smhi", "failed")

    return msg


def marvinStrip(row, asList=None, asStr=None):
    """
    Get a comic strip.
    """
    msg = None
    if row.intersection(['strip', 'comic', 'nöje', 'paus']):
        if row.intersection(['rand', 'random', 'slump', 'lucky']):
            msg = commitStrip(randomize=True)
        else:
            msg = commitStrip()

    return msg


def commitStrip(randomize=False):
    """
    Latest or random comic strip from CommitStrip.
    """
    msg = getString("commitstrip", "message")

    if randomize:
        first = getString("commitstrip", "first")
        last = getString("commitstrip", "last")
        rand = random.randint(first, last)
        url = getString("commitstrip", "urlPage") + str(rand)
    else:
        url = getString("commitstrip", "url")

    return msg.format(url=url)


#      elif ('latest' in row or 'senaste' in row or 'senast' in row)
# and ('forum' in row or 'forumet' in row):
#        feed=feedparser.parse(FEED_FORUM)


def marvinTimeToBBQ(row, asList=None, asStr=None):
    """
    Calcuate the time to next barbecue and print a appropriate msg
    """
    msg = None
    if row.intersection(['grilla', 'grill', 'grillcon', 'bbq']):
        url = getString("barbecue", "url")
        nextDate = nextBBQ()
        today = datetime.date.today()
        daysRemaining = (nextDate - today).days

        if daysRemaining == 0:
            msg = getString("barbecue", "today")
        elif daysRemaining == 1:
            msg = getString("barbecue", "tomorrow")
        elif daysRemaining < 14 and daysRemaining > 0:
            msg = getString("barbecue", "week") % nextDate
        elif daysRemaining < 200 and daysRemaining > 0:
            msg = getString("barbecue", "base") % nextDate
        else:
            msg = getString("barbecue", "eternity") % nextDate

        return url + ". " + msg


def nextBBQ(after=datetime.date.today()):
    """
    Calculate the next grillcon date after a given date (or from today)
    """
    MAY = 5
    SEPTEMBER = 9

    spring = thirdFridayIn(after.year, MAY)
    if after <= spring:
        return spring

    autumn = thirdFridayIn(after.year, SEPTEMBER)
    if after <= autumn:
        return autumn

    return thirdFridayIn(after.year + 1, MAY)


def thirdFridayIn(y, m):
    """
    Get the third Friday in a given month and year
    """
    THIRD = 2
    FRIDAY = -1

    # Start the weeks on saturday to prevent fridays from previous month
    cal = calendar.Calendar(firstweekday=calendar.SATURDAY)

    # Return the friday in the third week
    return cal.monthdatescalendar(y, m)[THIRD][FRIDAY]


def marvinBirthday(row, asList=None, asStr=None):
    """
    Check birthday info
    """
    msg = None
    if row.intersection(['birthday', 'födelsedag']):
        try:
            url = getString("birthday", "url")
            soup = BeautifulSoup(urlopen(url), "html.parser")
            my_list = list()

            for ana in soup.findAll('a'):
                if ana.parent.name == 'strong':
                    my_list.append(ana.getText())

            my_list.pop()
            my_strings = ', '.join(my_list)
            if not my_strings:
                msg = getString("birthday", "nobody")
            else:
                msg = getString("birthday", "somebody").format(my_strings)

        except Exception:
            msg = getString("birthday", "error")

        return msg

def marvinNameday(row, asList=None, asStr=None):
    """
    Check current nameday
    """
    msg = getString("nameday", "nobody")
    if row.intersection(['nameday', 'namnsdag']):
        try:
            now = datetime.datetime.now()
            raw_url = "http://api.dryg.net/dagar/v2.1/{year}/{month}/{day}"
            url = raw_url.format(year=now.year, month=now.month, day=now.day)
            r = requests.get(url)
            nameday_data = r.json()
            name = ",".join(nameday_data["dagar"][0]["namnsdag"])
            msg = getString("nameday", "somebody").format(name)
        except Exception:
            msg = getString("nameday", "error")
        return msg

def marvinUptime(row, asList=None, asStr=None):
    """
    Display info about uptime tournament
    """
    msg = None
    if row.intersection(['uptime']):
        msg = getString("uptime", "info")
        return msg

def marvinStream(row, asList=None, asStr=None):
    """
    Display info about stream
    """
    msg = None
    if row.intersection(['stream', 'streama', 'ström', 'strömma']):
        msg = getString("stream", "info")
        return msg

def marvinPrinciple(row, asList=None, asStr=None):
    """
    Display one selected software principle, or provide one as random
    """
    if row.intersection(['principle', 'princip', 'principer']):
        principles = getString("principle")
        key = row.intersection(list(principles.keys()))
        if key:
            return principles[key.pop()]
        return principles[random.choice(list(principles.keys()))]

def getJoke():
    """
    Retrieves joke from api.icndb.com/jokes/random?limitTo=[nerdy]
    """
    try:
        url = getString("joke", "url")
        soup = urlopen(url)
        rawData = soup.read()
        encoding = soup.info().get_content_charset('utf8')
        joke = json.loads(rawData.decode(encoding))
        return joke["value"]["joke"]
    except Exception:
        return getString("joke", "error")

def marvinJoke(row, asList=None, asStr=None):
    """
    Display a random Chuck Norris joke
    """
    msg = None
    if row.intersection(["joke", "skämt", "chuck norris", "chuck", "norris"]):
        msg = getJoke()
        return msg

def getCommit():
    """
    Retrieves random commit message from whatthecommit.com/index.html
    """
    try:
        url = getString("commit", "url")
        r = requests.get(url)
        res = r.text.strip()
        return res
    except Exception:
        return getString("commit", "error")

def marvinCommit(row, asList=None, asStr=None):
    """
    Display a random commit message
    """
    commitMsg = "Use this message: '{}'"
    msg = None
    if row.intersection(["commit", "-m"]):
        msg = getCommit()
        return commitMsg.format(msg)
