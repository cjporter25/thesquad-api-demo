import requests
from threading import Event

# Member Info Gathering: Requests player account information via a provided
#   summoner name (if valid). This data is then manually parsed into a 
#   proprietarily designed list of ID's to then be used inside a squad object
def get_player_info(riot_id, apiKey):
    new_riot_id = replace_spaces_with_percent20(riot_id)
    # print("Updated Riot ID: " + new_riot_id)
    IDandTag = parse_id_and_tag(new_riot_id)
    # print("Parsed RiotID: " + IDandTag[0] + " and " + IDandTag[1])
    api_url_riot_id = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + IDandTag[0]
    # print(api_url_riot_id)
    api_url_plus_key = api_url_riot_id + "/" + IDandTag[1] + "?api_key=" + apiKey
    # print(api_url_plus_key)
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()
    puuID = summ_info['puuid']

    api_url_puuid = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuID
    api_url_plus_key = api_url_puuid + '?api_key=' + apiKey
    request_resp = requests.get(api_url_plus_key)
    summ_info = request_resp.json()

    name = riot_id
    acctId = summ_info['accountId']
    id = summ_info['id']
    lvl = str(summ_info['summonerLevel'])
    # puuId = player_info['puuid']
    player_info = [name, acctId, id, lvl, puuID]
    return player_info

def replace_spaces_with_percent20(riot_id):
    return riot_id.replace(' ', '%20')
def parse_id_and_tag(input_id):
    if '#' in input_id:
        parts = input_id.split('#')
        id = parts[0]
        tag = parts[1]
        return [id, tag]
    else:
        return [input_id, 'NA1']
    

#Match History Gathering: Uses (and only works with) player puu_id and API key. 
#   Returns list of 20 most recently play games.
#   List ranges from 0-19 with matchHistory[0] being the most recent match.
def get_match_history(player_puuID, count, apiKey):
    api_url_puuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + player_puuID
    api_urlkey = api_url_puuid + "/ids?start=0&count=" + count + "&api_key=" + apiKey
    reqResp = requests.get(api_urlkey)
    player_matchHistory = reqResp.json()
    return player_matchHistory

# Added as a one-time request. In "find_shared_matches()", it can parse
#   the return value of this instead of making a request twice - once
#   for metadata, and once for info (like it was setup below).
# The incoming response body as a parseable Metadata and Info Section. The gameMode
#   key is located in Info. These are all manually iterable as needed in a squad.
def get_match(matchID, apiKey):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchID
    api_urlkey = api_url_matchId + '?api_key=' + apiKey
    reqResp = requests.get(api_urlkey)
    matchInfo = reqResp.json()
    return matchInfo

# Gather Match Metadata: Request data based on MatchID. Parse for the "Metadata"
#   section. Return the "Metadata" section only
# UPDATE: Only used for testing to reduce overall requests made in main
def get_match_metadata(matchID, apiKey):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchID
    api_urlkey = api_url_matchId + '?api_key=' + apiKey
    reqResp = requests.get(api_urlkey)
    matchMetaData = reqResp.json()
    return matchMetaData['metadata']

# Gather Match Metadata: Request data based on MatchID. Parse for the "Info"
#   section. Return the "info" section only
# UPDATE: Only used for testing to reduce overall requests made in main
def get_match_info(matchID, apiKey):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchID
    api_urlkey = api_url_matchId + '?api_key=' + apiKey
    reqResp = requests.get(api_urlkey)
    matchInfo = reqResp.json()
    return matchInfo['info']

# Gather Match GameMode: Request data based on MatchID. Parse for the "gameMode" 
#   key in the response body. Return the gameMode
# UPDATE: Only used for testing to reduce overall requests made in main
def get_match_gamemode(matchID, apiKey):
    matchInfo = get_match_info(matchID, apiKey)
    return matchInfo['gameMode']

# Uses metadata to find the players' order in that match ->
#    This is done by comparing input puuId's with the metadata list
# Pulls data set from matchinfo based on player's position in the order
def get_player_match_info(matchInfo, matchMetaData, playerPuuID):
    #MetaData key - "participants" - contains full participants list. Obtain this list
    matchPlayerList = matchMetaData['participants']
    #Safe to use Index method as every player puuID is guaranteed unique.
    #   It then returns the index value for the player in the list
    pListPosition = matchPlayerList.index(playerPuuID)
    #Return all match specific metrics for this player
    return matchInfo['participants'][pListPosition]

def get_enemy_team_info(matchInfo, matchMetaData, puuIDList):
    pList = matchMetaData['participants']
    enemyTeamComp = []
    squadIsBottom = True
    for puuID in puuIDList:
        pListPosition = pList.index(puuID)
        if pListPosition >= 5:
            squadIsBottom = False
    if squadIsBottom:
        # Our squad is on the bottom of the list of participants, therefore, the
        #   enemy team is contained in the indexes of 5-9.
        for pListPosition in range(5, 10):
            currEnemyInfo = matchInfo['participants'][pListPosition]
            enemyTeamComp.append(currEnemyInfo['championName'])
    else:
        # Our squad is on the top of the list of participants, therefore, the
        #   enemy team is contained in the indexes of 0-4.
        for pListPosition in range(5):
            currEnemyInfo = matchInfo['participants'][pListPosition]
            enemyTeamComp.append(currEnemyInfo['championName'])

    #print(enemyTeamComp)
    return enemyTeamComp


