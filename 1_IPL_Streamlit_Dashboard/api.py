from flask import Flask, request, jsonify
from ipl import IPL

app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/api/teams')
def teams():
    teams = ipl.allTeams_API()
    return jsonify(teams)

@app.route('/api/allPlayers')
def all_players():
    players = ipl.allPlayers_API()
    return jsonify(players)

@app.route('/api/teamPlayers')
def team_players():
    team = request.args.get('team')
    players = ipl.teamPlayers_API(team)
    return jsonify(players)

@app.route('/api/teamRecord')
def team_record():
    team = request.args.get('team')
    response = ipl.teamRecord_API(team)
    return jsonify(response)

@app.route('/api/batsmanRecord')
def batsman_record():
    batsman = request.args.get('batsman')
    response = ipl.batsmanRecord_API(batsman)
    return jsonify(response)

@app.route('/api/bowlerRecord')
def bowler_record():
    bowler = request.args.get('bowler')
    response = ipl.bowlerRecord_API(bowler)
    return jsonify(response)



if __name__ == '__main__':
    ipl_matches = "./data/IPL_Matches_2008_2022.csv" or "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
    ipl_balls = "data/IPL_Ball_by_Ball_2008_2022.csv" or "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
    ipl = IPL(ipl_matches, ipl_balls)
    
    app.run(debug=True)
