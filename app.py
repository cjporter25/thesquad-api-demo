import requests

from flask import Flask, request, jsonify, render_template

from app_util import *

#### WEBSITE LINK ####
# https://thesquad-api-0958e48e01c7.herokuapp.com/ #

# TO RUN LOCALLY: python -m flask run   

# from datetime import datetime --> Now imported from firebase module
# from ts_riot_api import KEY --> KEYS are now setup as environment vars
# from util import generate_new_key --> Uneeded, will implement in later stages

# Establish reference name for Flask
app = Flask(__name__)

#### RETURNING STORED KEYS "_" characters to "-" ####
riot_key = retrieve_riot_api_key()
#####################################################

############### INITIALIZING FIREBASE ###############
update_firebase_cred()
initialize_firebase()
clear_firebase_cred()
####################################################

@app.route("/")
def index():
    return render_template('index.html')
    #return "WORK IN PROGRESS... This will eventually have API usage instructions"

@app.route("/hello/")
def hello():
    return "GAMER WORDS"

# Usage: www.thesquadapi.com/get-player-info/<summoner_name>
@app.route("/get-player-info/<summoner_name>")
def get_player_info(summoner_name):
    api_url_summName = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name
    api_url_plus_key = api_url_summName + '?api_key=' + riot_key
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()

    player_info = {
        "name": summ_info['name'],
        "acctID": summ_info['accountId'],
        "id": summ_info['id'],
        "lvl":  str(summ_info['summonerLevel']),
        "puuID": summ_info['puuid']  
    }
    #player_info_json = json.dumps(player_info)
    return jsonify(player_info), 200

# Usage: www.thesquadapi.com/get-match-history/<summoner_name>/?count=<num>
@app.route("/get-match-history/<summoner_name>/")
def get_match_history_name(summoner_name):
    count = request.args.get("count", default="20", type=str)
    api_url_summName = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name
    api_url_plus_key = api_url_summName + '?api_key=' + riot_key
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()
    puuid = summ_info['puuid']

    api_url_puuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid
    api_urlkey = api_url_puuid + "/ids?start=0&count=" + count + "&api_key=" + riot_key
    reqResp = requests.get(api_urlkey)
    player_matchHistory = reqResp.json()
    return player_matchHistory, 200

# Usage: www.thesquadapi.com/get-match-history/<puuid>/?count=<num>
@app.route("/get-match-history/<puuid>/")
def get_match_history_puuid(puuid):
    count = request.args.get("count", default="20", type=str)
    api_url_puuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid
    api_urlkey = api_url_puuid + "/ids?start=0&count=" + count + "&api_key=" + riot_key
    reqResp = requests.get(api_urlkey) # "Request Response"
    player_matchHistory = reqResp.json()
    return player_matchHistory, 200

# Usage: www.thesquadapi.com/get-match-data/<matchid>/
@app.route("/get-match-data/<matchid>/")
def get_match_data(matchid):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchid
    api_urlkey = api_url_matchId + '?api_key=' + riot_key
    reqResp = requests.get(api_urlkey)
    matchData = reqResp.json()
    return matchData

# Usage: www.thesquadapi.com/check-squadid-id/<squadid>/
@app.route("/check-squad-id/<squadid>")
def check_squad_id(squadid):
    #update_firebase_cred()
    #initialize_firebase()
    #clear_firebase_cred()
    db = firestore.client()
    squadIDList = db.collection(u'TheSquad').document(u'SquadID')
    list = squadIDList.get().to_dict()
    if squadid in list:
        return "The squad id: " + squadid + " does exist!"
    else: 
        return "The squad id: " + squadid + " does NOT exist!"

# Usage: www.thesquadapi.com/get-squad-data/?p1=<name>&p2=<name>&...
# 3MAN LOCAL --> 
# /retrieve-squad-data/?p0=Shensëi&p1=PureLunar&p2=Serandipityyy
# 4MAN LOCAL -->
# /retrieve-squad-data/?p0=Chrispychickn25&p1=PureLunar&p2=Serandipityyy&p3=Shensëi
@app.route("/retrieve-squad-data/")
def retrieve_squad_data():
    p0 = request.args.get("p0", default="N/A", type=str)
    p1 = request.args.get("p1", default="N/A", type=str)
    p2 = request.args.get("p2", default="N/A", type=str)
    p3 = request.args.get("p3", default="N/A", type=str)
    p4 = request.args.get("p4", default="N/A", type=str)
    inputList = [p0, p1, p2, p3, p4]
    empty = "N/A"
    squadMembers = [i for i in inputList if i != empty]

    squad = Squad()
    #squad.set_member_list(squadMembers)
    #savedList = squad.get_member_list()
    #squad.show_member_list()

    #squad.gather_squad_member_info(riot_key)
    #savedInfo = squad.get_member_info()

    squad.initialize(squadMembers, REC_MATCH_HISTORY_COUNT, riot_key)
    sqData = json.dumps(squad.get_squad_data(), indent=2)
    return sqData, 200
    #return savedInfo, 200
    
    # Create a dictionary object that adds various syntax errors
    #   if an error is spotted, flag it, and return the total
    #   error message at the end.

# Usage: www.thesquadapi.com/testenv/
@app.route("/testenv/")
def test_env():
    squad1 = Squad()
    squad1Start = time.time()
    squad1.set_member_list(TEST_SQUAD_LIST_01)
    squad1.gather_squad_member_info(riot_key)
    squad1.create_squad_id()
    squad1.gather_squad_match_history(str(20), riot_key)
    squad1.find_shared_matches(riot_key)
    squad1.show_shared_match_history()
    squad1End = time.time()
    squad2 = Squad()
    squad2Start = time.time()
    squad2.set_member_list(TEST_SQUAD_LIST_01)
    squad2.gather_squad_member_info(riot_key)
    squad2.create_squad_id()
    squad2.gather_squad_match_history(str(20), riot_key)
    squad2.EXP_find_shared_matches(riot_key)
    squad2.show_shared_match_history()
    squad2End = time.time()

    totalSquad1Time = round((squad1End - squad1Start), 2)
    print("Squad 1 Time: " + str(totalSquad1Time))
    totalSquad2Time = round((squad2End - squad2Start), 2)
    print("Squad 2 Time: " + str(totalSquad2Time))

    return "CHECK OUTPUT BITCH", 200


#@app.route("/generate-new-api-key/<username>")
#def generate_new_api_key(username):
#    userkey = generate_new_key(username)
#    return userkey, 200

if __name__ == "__main__":
    app.run(debug=False)