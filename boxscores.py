from flask import Flask, render_template, request

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

    dates = [date + datetime.timedelta(days=i) for i in range(-2, 3)]
    dates = [date.strftime('%Y%m%d') for date in dates]
    current_date = date.strftime('%Y%m%d')
    date = date.strftime('%Y%m%d')

    json = get_scoreboard_json(date)

    return render_template('scoreboard.html', dates=dates, games=json['games'])

@app.route('/boxscore/<date>/<gameid>', defaults={'size': None})
@app.route('/boxscore/<date>/<gameid>/<size>')
def show_boxscore(date, gameid, size):
    boxscore = get_boxscore_json(date, gameid)

    if 'stats' not in boxscore:
        return 'Game has not started'

    players_json = get_players_json(boxscore['basicGameData']['seasonYear'])

    for player in boxscore['stats']['activePlayers']:
        for record in players_json['league']['standard']:
            if record['personId'] == player['personId']:
                player['playerName'] = record['firstName'] + ' ' + record['lastName']
                player['pos'] = record['pos']
                
    if size is None and 'Android' in request.headers['User-Agent']:
        size = 'compact'

    if size == 'compact' :
        template = 'boxscore-mobile.html'
    elif size == 'full':
        template = 'boxscore.html'
    else:
        template = 'boxscore.html'

    return render_template(template, boxscore=boxscore)

@app.route('/standings')
def show_standings():
    date = datetime.datetime.today().strftime('%Y%m%d')

    standings = get_standings_json(date)
    teams = get_teams_json(standings['league']['standard']['seasonYear'])
    teams = {team['teamId']: team['tricode'] for team in teams['league']['standard']}

    return render_template('standings.html', standings=standings, teams=teams)

@app.route('/schedule/<year>/<teamid>')
def show_schedule(year, teamid):
    schedule = get_schedule_json(year, teamid)
    teams = get_teams_json(year)

    return render_template('schedule.html', schedule=schedule, teamid=teamid, teams=teams)

def get_boxscore_json(date, gameid):
    url = 'https://data.nba.net/prod/v1/{}/{}_boxscore.json'.format(date, gameid)
    return request_and_decode(url)

def get_players_json(year):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/players.json'.format(year)
    return request_and_decode(url)

def get_teams_json(year):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/teams.json'.format(year)
    return request_and_decode(url)

def get_scoreboard_json(date):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/scoreboard.json'.format(date)
    return request_and_decode(url)

def get_standings_json(date):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/standings_conference.json'.format(date)
    return request_and_decode(url)

def get_schedule_json(year, teamid):
    url = 'http://data.nba.net/data/10s/prod/v1/{}/teams/{}/schedule.json'.format(year, teamid)
    return request_and_decode(url)

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
