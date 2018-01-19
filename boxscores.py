from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def boxscore():
    boxscore = []
    json = get_boxscore_json()
    header = clean_boxscore_row(json['resultSets'][0]['headers'])

    for player_row in json['resultSets'][0]['rowSet']:
        boxscore.append(clean_boxscore_row(player_row))

    return render_template('boxscore.html', header=header, boxscore=boxscore)

# eventually this will pull json directly from the nba api
def get_boxscore_json():
    with open('static/0021600622_boxscore.json', 'r') as f:
        boxscore = json.load(f)

    return boxscore

def clean_boxscore_row(row):
    cols = [0, 1, 3, 4, 6, 7]

    for i in reversed(cols):
        del row[i]

    return row
