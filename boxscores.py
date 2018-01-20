from flask import Flask, render_template

import json
import urllib.request
import gzip
import datetime

app = Flask(__name__)

headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Referer": "http://stats.nba.com/scores/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Origin": "http://stats.nba.com",
}

@app.route('/', defaults={'date': None})
@app.route('/<date>')
def show_scoreboard(date):
    if date is None:
        date = datetime.datetime.today()
    else:
        date = datetime.datetime.strptime(date, '%Y%m%d')

    dates = [date + datetime.timedelta(days=i) for i in range(-3, 4)]
    dates = [date.strftime('%Y%m%d') for date in dates]
    date = date.strftime('%m/%d/%Y')

    json = get_scoreboard_json(date)
    indexes = [2, 4, 22]
    rows = json['resultSets'][1]['rowSet']

    games = []

    for row in rows:
        games.append([row[i] for i in indexes])

    return render_template('scoreboard.html', dates=dates, games=games)

@app.route('/boxscore/<gameid>')
def show_boxscore(gameid):
    boxscore = []
    json = get_boxscore_json(gameid)
    header = clean_boxscore_row(json['resultSets'][0]['headers'])

    for player_row in json['resultSets'][0]['rowSet']:
        boxscore.append(clean_boxscore_row(player_row))

    return render_template('boxscore.html', header=header, boxscore=boxscore)

def get_boxscore_json(gameid):
    url = 'http://stats.nba.com/stats/boxscoretraditionalv2?gameid={}&startperiod=1&endperiod=10&startrange=0&endrange=2147483647&rangetype=2'.format(gameid)

    req = urllib.request.Request(url, headers=headers)
    resp_bytes = gzip.decompress(urllib.request.urlopen(req).read())
    boxscore = json.loads(resp_bytes.decode('utf-8'))

    return boxscore

def get_scoreboard_json(date):
    url = 'http://stats.nba.com/stats/scoreboardV2?gamedate={}&leagueid=00&dayoffset=0'.format(date)

    req = urllib.request.Request(url, headers=headers)
    resp_bytes = gzip.decompress(urllib.request.urlopen(req).read())
    scoreboard = json.loads(resp_bytes.decode('utf-8'))
    
    return scoreboard

def clean_boxscore_row(row):
    cols = [0, 1, 3, 4, 6, 7]

    for i in reversed(cols):
        del row[i]

    return row
