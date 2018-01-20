from flask import Flask, render_template

import json
import urllib.request
import gzip

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
    json = get_scoreboard_json(date)
    indexes = [2, 4]
    rows = json['resultSets'][1]['rowSet']
    games = list(set([row[2] for row in rows]))

    return render_template('scoreboard.html', games=games)

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
    with open('static/01182018_scoreboard.json', 'r') as f:
        scoreboard = json.load(f)

    return scoreboard

def clean_boxscore_row(row):
    cols = [0, 1, 3, 4, 6, 7]

    for i in reversed(cols):
        del row[i]

    return row
