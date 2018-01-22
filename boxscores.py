from flask import Flask, render_template

import json
import urllib.request
import gzip
import datetime

app = Flask(__name__)

@app.route('/', defaults={'date': None})
@app.route('/<date>')
def show_scoreboard(date):
    if date is None:
        date = datetime.datetime.today()
    else:
        date = datetime.datetime.strptime(date, '%Y%m%d')

    dates = [date + datetime.timedelta(days=i) for i in range(-3, 4)]
    dates = [date.strftime('%Y%m%d') for date in dates]
    current_date = date.strftime('%Y%m%d')
    date = date.strftime('%Y%m%d')

    json = get_scoreboard_json(date)

    return render_template('scoreboard.html', dates=dates, games=json['games'])

@app.route('/boxscore/<date>/<gameid>')
def show_boxscore(date, gameid):
    json = get_boxscore_json(escape(date), date(gameid))

    if 'stats' not in json:
        return 'Game has not started'

    teams = [[json['basicGameData']['vTeam']['teamId'], json['basicGameData']['vTeam']['triCode']],
             [json['basicGameData']['hTeam']['teamId'], json['basicGameData']['hTeam']['triCode']]]

    players_json = get_players_json()
    players = json['stats']['activePlayers']

    for player in players:
        player_record = next(record for record in players_json['league']['standard'] if record['personId'] == player['personId'])
        player['playerName'] = player_record['firstName'] + ' ' + player_record['lastName']
        player['pos'] = player_record['pos']

    boxscore = { teams[0][0]: [clean_boxscore_row(row) for row in json['stats']['activePlayers'] if row['teamId'] == teams[0][0]],
                 teams[1][0]: [clean_boxscore_row(row) for row in json['stats']['activePlayers'] if row['teamId'] == teams[1][0]] }

    return render_template('boxscore.html', teams=teams, boxscore=boxscore)

def get_boxscore_json(date, gameid):
    url = 'https://data.nba.net/prod/v1/{}/{}_boxscore.json'.format(date, gameid)
    return request_and_decode(url)

def get_players_json():
    #TODO: populate year dynamically
    year = 2017
    url = 'http://data.nba.net/data/10s/prod/v1/{}/players.json'.format(year)
    return request_and_decode(url)

def get_scoreboard_json(date):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/scoreboard.json'.format(date)
    return request_and_decode(url)

def clean_boxscore_row(row):
    cols = ['playerName', 'pos', 'min', 'fgm', 'fga', 'fgp', 'ftm', 'fta', 'ftp', 'tpm', 'tpa', 'tpp', 'offReb', 'defReb', 'totReb', 'assists', 'steals', 'blocks', 'turnovers', 'pFouls', 'plusMinus', 'points']

    return [row[x] for x in cols]

def request_and_decode(url):
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

    req = urllib.request.Request(url, headers=headers)
    resp_bytes = gzip.decompress(urllib.request.urlopen(req).read())
    return json.loads(resp_bytes.decode('utf-8'))
