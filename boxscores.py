from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def boxscore():
    json = get_boxscore_json()

    boxscore = []
    boxscore.append(json['resultSets'][0]['headers'])

    for player_row in json['resultSets'][0]['rowSet']:
        boxscore.append(player_row)

    return render_template('boxscore.html', boxscore=boxscore)

# eventually this will pull json directly from the nba api
def get_boxscore_json():
    with open('static/0021600622_boxscore.json', 'r') as f:
        boxscore = json.load(f)

    return boxscore
