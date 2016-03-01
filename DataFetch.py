# DataFetch gets statistics about teams from ESPN and structures it within a database for use in a meaningful way
# Author: Marshall Mueller
# Date created: 3/1/2016
# Last Modified: 3/1/2016

from bs4 import BeautifulSoup
import requests
from BTrees.OOBTree import OOBTree
from ZODB import FileStorage, DB
import transaction
from persistent import Persistent

storage = FileStorage.FileStorage("teams.fs")
db = DB(storage)
conn = db.open()
dbroot = conn.root()

if not dbroot.has_key("teams"):
    dbroot["teams"] = OOBTree()

teamsList = dbroot["teams"]


class Team(Persistent):
    def __init__(self, name, statsUrl):
        self.name = name
        self.statsUrl =statsUrl

    def update(self):
        response2 = requests.get("http://espn.go.com" + self.statsUrl)
        soup2 = BeautifulSoup(response2.text, 'html5lib')
        totals = soup2.find("tr", {"class" : "total"})
        self.ppg = totals.findAll("td")[3].text.strip()
        subtitle = soup2.find("div", {"class", "sub-title"})
        subtitle = subtitle.text.strip()
        record = subtitle[:subtitle.index(",")]
        self.wins = record[:record.index("-")]
        self.losses = record[record.index("-") + 1:]

if len(teamsList) == 0:
    url = "http://espn.go.com/mens-college-basketball/teams"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html5lib')
    container = soup.find("div", {"class" : "span-4"})
    teamURLs = container.findAll("li")

    for teamURL in teamURLs:
        links = teamURL.findAll("a")
        name = links[0].text.strip()
        statsUrl = links[1]['href']
        team = Team(name, statsUrl)
        team.update()
        teamsList[name] = team

        transaction.commit()
        print "Team: " + team.name + " wins: " + team.wins + "\n"
else:
    for teamName in teamsList:
        print teamName + ", wins: " + teamsList[teamName].wins + '\n'