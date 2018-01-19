from flask import Flask, render_template
import json

app = Flask(__name__)

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

# eventually this will pull json directly from the nba api
def get_boxscore_json(gameid):
    with open('static/0021600622_boxscore.json', 'r') as f:
        boxscore = json.load(f)

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
