import requests

from flask import Flask, request, jsonify, render_template

from app_util import *

#### WEBSITE LINK ####
# https://thesquad-api-0958e48e01c7.herokuapp.com/ #

# TO RUN LOCALLY: python -m flask run   

# Establish reference name for Flask
app = Flask(__name__)

#### RETURNING STORED KEYS "_" characters to "-" ####
riot_key = retrieve_riot_api_key()
#####################################################

############### INITIALIZING FIREBASE ###############
# print("Updating Firebase Credentials...")
update_firebase_cred()
# print("Initializing Firebase")
initialize_firebase()
# print("Clearing Firebase Credentials")
clear_firebase_cred()
####################################################

@app.route("/")
def index():
    return render_template('home.html')
    #return base webpage

@app.route("/hello/")
def hello():
    squad1 = Squad()
    squad1.ARAM_match_data_repair(TEST_SQUAD_LIST_01, riot_key)
    return "Hello!"

# Usage: www.thesquad-api.com/repair-match-data/?p1=<name>&p2=<name>&...
# 3MAN LOCAL --> 
# localhost:5000/repair-match-data-ARAM/?p0=PureLunar%23NA1&p1=La%20Migra%20Oficial%236362&p2=Serandipityyy%23NA1
# localhost:5000/repair-match-data-ARAM/?p0=Chrispychickn25%23NA1&p1=PureLunar%23NA1&p2=Serandipityyy%23NA1
@app.route("/repair-match-data-ARAM/")
def repair_match_data_ARAM():
    p0 = request.args.get("p0", default="N/A", type=str)
    p1 = request.args.get("p1", default="N/A", type=str)
    p2 = request.args.get("p2", default="N/A", type=str)
    p3 = request.args.get("p3", default="N/A", type=str)
    p4 = request.args.get("p4", default="N/A", type=str)

    inputList = [p0, p1, p2, p3, p4]
    empty = "N/A"
    squadMembers = [i for i in inputList if i != empty]

    squad1 = Squad()
    squad1.ARAM_match_data_repair(squadMembers, riot_key)

    return "repair was succesful"

# Usage: www.thesquad-api.com/get-player-info/<summonerName>
# Ex: localhost:5000/get-player-info/Chrispychickn25
@app.route("/get-player-info/<summonerName>")
def get_player_info(summonerName):
    api_url_summName = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName
    api_url_plus_key = api_url_summName + '?api_key=' + riot_key
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()

    player_info = {
        "name": summonerName,
        "acctID": summ_info['accountId'],
        "id": summ_info['id'],
        "lvl":  str(summ_info['summonerLevel']),
        "puuID": summ_info['puuid']  
    }
    return jsonify(player_info), 200

# Usage: www.thesquad-api.com/get-player-info/by-riot-id/<riot_id>/?tagline=<string>
# Ex: localhost:5000/get-player-info/by-riot-id/Chrispychickn25/?tagline=NA1
@app.route("/get-player-info/by-riot-id/<riot_id>/")
def get_player_info_riotID(riot_id):
    tagline = request.args.get("tagline", default="NA1", type=str)
    api_url_riot_id = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + riot_id
    api_url_plus_key = api_url_riot_id + "/" + tagline + '?api_key=' + riot_key
 # EX: "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Chrispychickn25/NA1?api_key=...
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()
    puuID = summ_info['puuid']
    
    api_url_puuid = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuID
    api_url_plus_key = api_url_puuid + '?api_key=' + riot_key
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()
    player_info = {
        "riotID": riot_id,
        "acctID": summ_info['accountId'],
        "id": summ_info['id'],
        "lvl":  str(summ_info['summonerLevel']),
        "puuID": puuID,  
        "tagline": tagline
    }
    return jsonify(player_info), 200

# Usage: www.thesquad-api.com/get-match-history/<riot_id>/?count=<num>&tagline=<string>
@app.route("/get-match-history/<riot_id>/")
def get_match_history_riotID(riot_id):
    count = request.args.get("count", default="20", type=str)
    tagline = request.args.get("tagline", default="NA1", type=str)
    api_url_riot_id = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + riot_id
    api_url_plus_key = api_url_riot_id + "/" + tagline + '?api_key=' + riot_key
 # EX: "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Chrispychickn25/NA1?api_key=...
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()
    puuID = summ_info['puuid']

    api_url_puuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuID
    api_urlkey = api_url_puuid + "/ids?start=0&count=" + count + "&api_key=" + riot_key
    reqResp = requests.get(api_urlkey)
    player_matchHistory = reqResp.json()
    return player_matchHistory, 200

# Usage: www.thesquad-api.com/get-match-history/<puuid>/?count=<num>
@app.route("/get-match-history/<puuid>/")
def get_match_history_puuid(puuid):
    count = request.args.get("count", default="20", type=str)
    api_url_puuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid
    api_urlkey = api_url_puuid + "/ids?start=0&count=" + count + "&api_key=" + riot_key
    reqResp = requests.get(api_urlkey) # "Request Response"
    player_matchHistory = reqResp.json()
    return player_matchHistory, 200

# Usage: www.thesquad-api.com/get-match-data/<matchid>/
# Local Usage: localhost:5000/get-match-data/NA1_4992595705
@app.route("/get-match-data/<matchid>/")
def get_match_data(matchid):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchid
    api_urlkey = api_url_matchId + '?api_key=' + riot_key
    reqResp = requests.get(api_urlkey)
    matchData = reqResp.json()
    return matchData

# Usage: www.thesquad-api.com/check-squad-id/<squadid>/
# Ex: localhost:5000/check-squad-id/8I_GBKGGSh_t_aJU
@app.route("/check-squad-id/<squadID>")
def check_squad_id(squadID):
    db = firestore.client()
    squadIDList = db.collection(u'TheSquad').document(u'SquadID')
    list = squadIDList.get().to_dict()
    if squadID in list:
        return jsonify({"squadID": squadID, "wasFound": True}), 200
    else: 
        return jsonify({"squadID": squadID, "wasFound": False}), 404

# Usage: www.thesquad-api.com/retrieve-squad-data/?p1=<name>&p2=<name>&...
@app.route("/retrieve-squad-data/")
def retrieve_squad_data():
    p0 = request.args.get("p0", default="N/A", type=str)
    p1 = request.args.get("p1", default="N/A", type=str)
    p2 = request.args.get("p2", default="N/A", type=str)
    p3 = request.args.get("p3", default="N/A", type=str)
    p4 = request.args.get("p4", default="N/A", type=str)

    inputList = [p0, p1, p2, p3, p4]
    empty = "N/A"
    # Remove anything from the list that is still "N/A"
    squadMembers = [i for i in inputList if i != empty]

    # It isn't a squad if it's only one person!
    # Return "Bad Request" response code w/ message
    if len(squadMembers) <= 1:
        return jsonify({"squadMembers": squadMembers, 
                        "message": "Squad not big enough!"}), 400 

    squad = Squad()
            #MIN_MATCH_HISTORY_COUNT = "0"
            #DEF_MATCH_HISTORY_COUNT = "20"
            #MID_MATCH_HISTORY_COUNT = "45"
            #REC_MATCH_HISTORY_COUNT = "90"
            #MAX_MATCH_HISTORY_COUNT = "100"
    squad.initialize(squadMembers, MID_MATCH_HISTORY_COUNT, riot_key)
    
    sqDataDICT = squad.get_squad_data()
    # Create a JSON formatted string of the squad's data set.
    sqDataJSON = json.dumps(sqDataDICT, indent=2)
    return sqDataJSON, 200

# Usage: www.thesquad-api.com/retrieve-squad-data-demo/?p1=<name>&p2=<name>&...
@app.route("/retrieve-squad-data-demo/")
def retrieve_squad_data_demo():
    p0 = request.args.get("p0", default="PureLunar#NA1", type=str)
    p1 = request.args.get("p1", default="La Migra Oficial#6362", type=str)
    p2 = request.args.get("p2", default="Serandipityyy#NA1", type=str)
    p3 = request.args.get("p3", default="N/A", type=str)
    p4 = request.args.get("p4", default="N/A", type=str)

    inputList = [p0, p1, p2, p3, p4]
    empty = "N/A"
    # Remove anything from the list that is still "N/A"
    squadMembers = [i for i in inputList if i != empty]

    # It isn't a squad if it's only one person!
    if len(squadMembers) <= 1:
        return "SquadList isn't big enough!"

    squad = Squad()
            #MIN_MATCH_HISTORY_COUNT = "0"
            #DEF_MATCH_HISTORY_COUNT = "20"
            #REC_MATCH_HISTORY_COUNT = "90"
            #MAX_MATCH_HISTORY_COUNT = "100"
    squad.initialize(squadMembers, REC_MATCH_HISTORY_COUNT, riot_key)
    
    squad_data = squad.get_squad_data()
    # Create a JSON formatted string of the squad's data set.
    return render_template('example-output.html', squad_data=squad_data)

# Usage: www.thesquad-api.com/testenv/
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


if __name__ == "__main__":
    app.run(debug=False)