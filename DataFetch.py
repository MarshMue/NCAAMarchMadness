# DataFetch gets statistics about teams from ESPN and structures it within a database for use in a meaningful way
# Author: Marshall Mueller
# Date created: 3/1/2016

from bs4 import BeautifulSoup
import requests
from BTrees.OOBTree import OOBTree
from ZODB import FileStorage, DB
import transaction
from persistent import Persistent

# storage = FileStorage.FileStorage("teams.fs")
# db = DB(storage)
# conn = db.open()
# dbroot = conn.root()
#
# if not dbroot.has_key("teams"):
#     dbroot["teams"] = OOBTree()
#
# Teams = dbroot["teams"]


class Team(Persistent):

    def __init__(self, name, statsUrl):
        self.name = name
        self.statsUrl = statsUrl
        self.players = []
        self.playerStats = {}
        self.ppg = 0
        self.wins = 0
        self.losses = 0

    def update(self):
        response2 = requests.get("http://espn.go.com" + self.statsUrl)
        soup2 = BeautifulSoup(response2.text, 'html5lib')
        container2 = soup2.find("div", {"class": "mod-content"})
        tr = container2.findAll("tr")
        index = 2
        while tr[index]["class"][0] != u'total':
            td = tr[index].findAll("td")
            self.players.append(td[0].text.strip())
            stats = {}
            statind = 1
            statname = tr[1].findAll("td")
            # convert stat column names to strings
            y = 0
            while y < len(statname):
                statname[y] = statname[y].text.strip()
                y += 1
                # get each player stats and add to stats dictionary, with stat name as key value
            while statind < len(tr[1]):
                statsrow = tr[index].findAll("td")
                stats[statname[statind]] = float(statsrow[statind].text.strip())
                statind += 1
            # add stats to player dictionary, indexed by plyer name
            self.playerStats[td[0].text.strip()] = stats
            index += 1
        # update team specific stats
        totals = soup2.find("tr", {"class": "total"})
        self.ppg = totals.findAll("td")[3].text.strip()
        subtitle = soup2.find("div", {"class", "sub-title"})
        subtitle = subtitle.text.strip()
        record = subtitle[:subtitle.index(",")]
        self.wins = record[:record.index("-")]
        self.losses = record[record.index("-") + 1:]

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
    # print for debug and verifying data
    print team.name
    for player in team.players:
        print player + ": " + str(team.playerStats[player])
    print ""
