# Standard  Library Imports
from datetime import datetime, date, timedelta
from operator import itemgetter
import time

# Firebase Imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Local App Imports
from thesquad.riot_api import *
from thesquad.constants import *

# IF NECESSARY TO SPACE OUT OUTPUT
#Event().wait(1)

# Specific firestore call that increments a reference value
INCREMENT = firestore.Increment(1)

#EXE_META_DATA = {
#                 'firebaseExeTime' : 0.00,
#                 'matchDataReqCount' : 0,
#                 'matchHistorySize': 0,
#                 'memDataReqCount' : 0,
#                 'memMatchHistoryReqCount' : 0,
#                 'numARAMMatchesPresent' : 0,
#                 'numARAMMatchesPushed' : 0,
#                 'numARAMSharedMatches' : 0,
#                 'numMembers' : 0, 
#                 'numSRMatchesPresent' : 0,
#                 'numSRMatchesPushed' : 0,
#                 'numSRSharedMatches' : 0,
#                 'projExeTime: 0.00,
#                 'squadExeTime' : 0.00,
#                 'squadExists' : False,
#                 'totalSharedMatches' : 0,
#                 }


def init_firebase():
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)
    print("****************************************************INITIALIZING APP********************************************************")

##################### START FIREBASE SECTION ################################

def check_squad_id(squadID, db):
    print("Looking for Squad ID in Database...")
    db = firestore.client()
    squadIDList = db.collection(u'TheSquad').document(u'SquadID')
    list = squadIDList.get().to_dict()
    doesSquadIDExist = squadID in list
    # If squad already exists, return TRUE
    if doesSquadIDExist:
        print("     SquadID already exists!")
        EXE_META_DATA['squadExists'] = doesSquadIDExist
        return doesSquadIDExist #TRUE
    # If squad doesn't exist, return FALSE
    else: 
        print("     SquadID does not yet exist, adding now!")
        EXE_META_DATA['squadExists'] = doesSquadIDExist
        return doesSquadIDExist #FALSE

def validate_summoner_names(squadID, puuIDList, memberInfo, db):
    for puuID in puuIDList:
        dataBuilder = db \
                .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
        memData = dataBuilder.get().to_dict()
        for member in memberInfo:
            newName = member[0]
            if ("summonerName" in memData):
                oldName = memData["summonerName"]
                if(puuID == member[4] and oldName != newName):
                    dataBuilder.set({u'summonerName': newName}, merge=True)
            else:
                dataBuilder.set({u'summonerName': newName}, merge=True)

def build_squad(squad, projStart):

    firebaseStart = time.time()

    #Initiate Firebase session
    db = firestore.client()
    # Obtain the input squad's id
    squadID = squad.get_squad_id()
    # Obtain the input squad's info
    memberInfo = squad.get_member_info()
    # Obtain the input squad's size
    squadSize = squad.get_squad_size()
    # Obtain the input squad's sharedMatchHistory
    sharedMatchHistory = squad.get_shared_match_history() 
    # Obtain the input squad's puuID list
    puuIDList = squad.retrieve_puuID_list()

    squadExists = check_squad_id(squadID, db)
    #Check for whether the squadID exists
    if squadExists:
        print("     Squad ID Exists. Updating Now...")
        validate_summoner_names(squadID, puuIDList, memberInfo, db)
        update_squad(squad, squadID, memberInfo, sharedMatchHistory, puuIDList, db)
    else:
        print("     Squad not in database. Adding squad using ID#: " + squadID)

        create_squad_data_set(squadID, squadSize, db)

        add_squad_members(squadID, memberInfo, db)
    
        add_squad_shared_match_lists(squadID, sharedMatchHistory, puuIDList, db)

        update_squad(squad, squadID, memberInfo, sharedMatchHistory, puuIDList, db)

    firebaseEnd = time.time()
    totalFirebaseTime = round((firebaseEnd - firebaseStart), 2)
    EXE_META_DATA['exeTimeFirebase'] = totalFirebaseTime
    totalProjTime = round((firebaseEnd - projStart), 2)
    EXE_META_DATA['exeTimeWhole'] = totalProjTime
    save_exe_meta_data(db)
    print("***Updated or Added Squad to Database Successfully***")
def create_squad_data_set(squadID, squadSize, db):
    # Use builder to create squadID/"ID"/squadData/
    squadDataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    squadDataBuilder.set(SQUAD_DATA)

    squadDataBuilder = db.document(u'TheSquad/SquadID')
    squadDataBuilder.set({
        squadID: squadSize
    }, merge=True)
def add_squad_members(squadID, memberInfo, db):
    #Retrieve current time to track what time squad was added
    currTime = get_current_time()
    #Retrieve current date to track what day squad was added
    currDate = get_current_date()
    # Use builder to create squadID/"ID"/squadMembers/... 
    sharedMatchBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') 
    sharedMatchBuilder.set({
        u'dateUpdated': currDate,
        u'timeUpdated' : currTime
    }, merge=True)

    # Use member data builder to create squadID/"ID"/squadMembers/memberData/...
    create_member_data_set(squadID, memberInfo, db)
    # Use member info builder to create squadID/"ID"/squadMembers/memberInfo/...
    add_member_info(squadID, memberInfo, db)
def add_member_info(squadID, memberInfo, db):
    print("Adding Member Info...")
    # For each member in the squad -->
    for member in memberInfo:
        # Create and reference their document inside "memberInfo" using their name
        playerInfoBuilder = db \
                        .document(u'TheSquad/SquadID') \
                        .collection(squadID) \
                        .document(u'SquadMembers') \
                        .collection(u'MemberInfo') \
                        .document(member[0])
        # Add necessary player information fields
        playerInfoBuilder.set({
            u'acctID': member[1],
            u'id': member[2],
            u'lvl': member[3],
            u'puuID': member[4]
        }, merge=True) 
def create_member_data_set(squadID, memberInfo, db):
    print("Building Member Data Set...")
    for member in memberInfo:
        squadBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(member[4])
        squadBuilder.set(MEMBER_DATA)
        squadBuilder.set({u'summonerName': member[0]}, merge=True)
def add_squad_shared_match_lists(squadID, sharedMatchHistory, puuIDList, db):
    print("Adding Shared Match Lists...")
    # Retrieve current time to track what time squad was added
    currTime = get_current_time()
    #Retrieve current date to track what day squad was added
    currDate = get_current_date()

    # Use builder to create squadID/"ID"/sharedMatchLists/...
    sharedMatchBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SharedMatchLists')
    sharedMatchBuilder.set({
        u'dateUpdated': currDate,
        u'timeUpdated' : currTime
    }, merge=True)

    # Use builder to create squadID/"ID"/sharedMatchLists/sharedARAMMatchList/...
    sharedMatchBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SharedMatchLists') \
                    .collection(u'SharedARAMMatchList') \
                    .document(u'NA_TEMP')
    sharedMatchBuilder.set({
        u'default': "N/A"
    }, merge=True)
    add_shared_ARAM_match_history(squadID, sharedMatchHistory, puuIDList, db)

    # Use builder to create squadID/"ID"/sharedMatchLists/sharedSRMatchList/...   
    sharedMatchBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SharedMatchLists') \
                    .collection(u'SharedSRMatchList') \
                    .document(u'NA_TEMP')
    sharedMatchBuilder.set({
        u'default': "N/A"
    }, merge=True)
    add_shared_SR_match_history(squadID, sharedMatchHistory, puuIDList, db)
def add_shared_ARAM_match_history(squadID, sharedMatchHistory, puuIDList, db):
    for matchID, matchData in sharedMatchHistory.items():
        gameMode = matchData['gameMode']
        if (gameMode == "ARAM"):
            matchListBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SharedMatchLists') \
                    .collection(u'SharedARAMMatchList') \
                    .document(matchID)
            newMatchData = {u'gameDuration' : matchData['gameDuration'],
                            u'gameMode': matchData['gameMode'],
                            u'readStatus': False
                            }
            for puuID in puuIDList:
                playerInfo = [matchData[puuID]['championName'], 
                              matchData[puuID]['win']]
                newMatchData[puuID] = playerInfo
                newMatchData['enemyTeam'] = matchData['enemyTeam']
            matchListBuilder.set(newMatchData, merge=True)  
def add_shared_SR_match_history(squadID, sharedMatchHistory, puuIDList, db):
    for matchID, matchData in sharedMatchHistory.items():
        gameMode = matchData['gameMode']
        if (gameMode == "CLASSIC"):
            matchListBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SharedMatchLists') \
                    .collection(u'SharedSRMatchList') \
                    .document(matchID)
            newMatchData = {u'gameDuration' : matchData['gameDuration'],
                            u'gameMode': matchData['gameMode'],
                            u'readStatus': False
                            }
            for puuID in puuIDList:
                playerInfo = [matchData[puuID]['championName'], 
                              matchData[puuID]['individualPosition'],
                              matchData[puuID]['lane'],
                              matchData[puuID]['role'],
                              matchData[puuID]['teamPosition'],
                              matchData[puuID]['win']]
                newMatchData[puuID] = playerInfo
            matchListBuilder.set(newMatchData, merge=True)

def update_squad(squad, squadID, memberInfo, sharedMatchHistory, puuIDList, db):
    # clear_all_member_data_sets(squadID, memberInfo, db)

    update_shared_ARAM_match_list(squadID, sharedMatchHistory, puuIDList, db)
    analyze_shared_ARAM_match_list(squadID, puuIDList, db)

    update_shared_SR_match_list(squadID, sharedMatchHistory, puuIDList, db)
    analyze_shared_SR_match_list(squadID, puuIDList, db)

    update_squad_ARAM_data_set(squadID, puuIDList, db)
    update_squad_SR_data_set(squadID, puuIDList, db)

    wrap_up(squadID, db)

    save_squad_data_to_squad(squad, db)

# Update the ARAM match list with new matches that are shared and haven't been added
#   yet.
def update_shared_ARAM_match_list(squadID, sharedMatchHistory, puuIDList, db):
    # Create constants for validation at the end of method
    matchesAlreadyAdded = []
    matchesToBeAdded = []
    # Stream and iterate through full ARAM matchID list saved in the database
    #   Create a local list to do so
    savedARAMList = []
    sharedARAMList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedARAMMatchList') \
                .stream()
    for matchID in sharedARAMList:
        if(matchID.id != "NA_TEMP"):
            savedARAMList.append(matchID.id)

    print("***Comparing incoming list to ARAM database list***")
    # Start comparison of gathered shared history to stored ARAM shared history
    for localMatchID in sharedMatchHistory:
        # Start each comparison by resetting matchFound to False
        matchInDatabase = False
        for savedMatchID in savedARAMList:
            # If the match is found, set matchInDatabase to TRUE. This indicates
            #   that we do not need to add this match again.
            if(savedMatchID == localMatchID):
                matchInDatabase = True
                matchesAlreadyAdded.append(localMatchID)
        # If the match has not been added yet, meaning the current matchID has not
        #   yet been saved to the database, go through the adding algorithm
        if(matchInDatabase == False):
            #print(enemyTeam)
            gameMode = sharedMatchHistory[localMatchID]['gameMode']
            gameDuration = sharedMatchHistory[localMatchID]['gameDuration']
            if (gameMode == "ARAM"):
                matchesToBeAdded.append(localMatchID)
                matchListBuilder = db \
                        .document(u'TheSquad/SquadID') \
                        .collection(squadID) \
                        .document(u'SharedMatchLists') \
                        .collection(u'SharedARAMMatchList') \
                        .document(localMatchID)
                newMatchData = {u'gameDuration' : gameDuration,
                                u'gameMode': gameMode,
                                u'readStatus': False}
                for puuID in puuIDList:
                    playerInfo = [sharedMatchHistory[localMatchID][puuID]['championName'], 
                                  sharedMatchHistory[localMatchID][puuID]['win']]
                    newMatchData[puuID] = playerInfo
                newMatchData['enemyTeam'] = sharedMatchHistory[localMatchID]['enemyTeam']
                matchListBuilder.set(newMatchData, merge=True)
    print("     Number ARAM matches already added from shared list-->" + str(len(matchesAlreadyAdded)))
    EXE_META_DATA['sharedARAMMatchesAlreadyPresent'] = len(matchesAlreadyAdded)
    print("     Number ARAM matches to be added -->" + str(len(matchesToBeAdded)))
    #EXE_META_DATA['sharedARAMMatchesPushed'] = len(matchesToBeAdded)
# Update each member's individual data sets by using the data found in the shared ARAM
#   match list. If the match's data was already added, it is skipped
def analyze_shared_ARAM_match_list(squadID, puuIDList, db):
    sharedARAMList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedARAMMatchList') \
                .stream()
    for matchID in sharedARAMList:
        if(matchID.id == "NA_TEMP"):
            return
        aramMatchData = matchID.to_dict()
        if(aramMatchData['readStatus'] == False):
            EXE_META_DATA['sharedARAMMatchesPushed'] += 1
            print("         Pushing ARAM Data from --> " + matchID.id)
            for id in aramMatchData:
                if(id in puuIDList):
                    champArch = get_champ_archetype(aramMatchData[id][0], db)
                    didMemberWin = aramMatchData[id][1]
                    update_member_ARAM_data(squadID, id, champArch, didMemberWin, db)
                    currMatch = db \
                            .document(u'TheSquad/SquadID') \
                            .collection(squadID) \
                            .document(u'SharedMatchLists') \
                            .collection(u'SharedARAMMatchList') \
                            .document(matchID.id)
                    #print("CURRENT MATCH = " + matchID.id)
                    currMatch.set({u'readStatus': True}, merge=True)
def update_member_ARAM_data(squadID, puuID, champArch, winStatus, db):
    trueChampArch = CHAMP_DATA_VALUES[champArch]
    matchesPlayedArch = "ARAM_matchesPlayed_" + trueChampArch
    matchesWonArch = "ARAM_matchesWon_" + trueChampArch
    matchesLostArch = "ARAM_matchesLost_" + trueChampArch
    winrateArch = "ARAM_winrate_" + trueChampArch
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
    if(winStatus == True):
        dataBuilder.update({
            matchesPlayedArch: INCREMENT,
            matchesWonArch: INCREMENT,
            "ARAM_totalMatchesPlayed" : INCREMENT,
            "ARAM_totalMatchesWon" : INCREMENT})
    if(winStatus == False):
        dataBuilder.update({
            matchesPlayedArch: INCREMENT,
            matchesLostArch: INCREMENT,
            "ARAM_totalMatchesPlayed" : INCREMENT,
            "ARAM_totalMatchesLost" : INCREMENT})
            
    newWinrate = update_member_ARAM_winrate(dataBuilder, matchesPlayedArch, matchesWonArch)
    dataBuilder.update({winrateArch: newWinrate})
def update_member_ARAM_winrate(dataBuilder, matchesPlayedArch, matchesWonArch):
    memberData = dataBuilder.get().to_dict()
    matchesPlayed = memberData[matchesPlayedArch]
    matchesWon = memberData[matchesWonArch]
    newWinrate = (matchesWon/matchesPlayed)
    newWinrate = round(newWinrate, 2)
    return newWinrate

# Update the SR match list with new matches that are shared and haven't been added
#   yet.
def update_shared_SR_match_list(squadID, sharedMatchHistory, puuIDList, db):
     # Create constants for validation at the end of method
    matchesAlreadyAdded = []
    matchesToBeAdded = []
    # Stream and iterate through full ARAM matchID list saved in the database
    savedSRList = []
    sharedSRList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedSRMatchList') \
                .stream()
    for matchID in sharedSRList:
        if(matchID.id != "NA_TEMP"):
            savedSRList.append(matchID.id)

    print("***Comparing incoming list to SR database list***")
    # Start comparison of gathered shared history to stored ARAM shared history
    for localMatchID in sharedMatchHistory:
        # Start each comparison by resetting matchFound to False
        matchInDatabase = False
        for savedMatchID in savedSRList:
            # If the match is found, set matchInDatabase to TRUE. This indicates
            #   that we do not need to add this match again.
            if(savedMatchID == localMatchID):
                matchInDatabase = True
                matchesAlreadyAdded.append(localMatchID)
        # If the match has not been added yet, meaning the current matchID has not
        #   yet been saved to the database, go through the adding algorithm
        if(matchInDatabase == False):
            gameMode = sharedMatchHistory[localMatchID]['gameMode']
            gameDuration = sharedMatchHistory[localMatchID]['gameDuration']
            if (gameMode == "CLASSIC"):
                matchesToBeAdded.append(localMatchID)
                matchListBuilder = db \
                        .document(u'TheSquad/SquadID') \
                        .collection(squadID) \
                        .document(u'SharedMatchLists') \
                        .collection(u'SharedSRMatchList') \
                        .document(localMatchID)
                newMatchData = {u'gameDuration' : gameDuration,
                                u'gameMode': gameMode,
                                u'readStatus': False}
                for puuID in puuIDList:
                    playerInfo = [sharedMatchHistory[localMatchID][puuID]['championName'],
                                  sharedMatchHistory[localMatchID][puuID]['individualPosition'],
                                  sharedMatchHistory[localMatchID][puuID]['lane'],
                                  sharedMatchHistory[localMatchID][puuID]['role'],
                                  sharedMatchHistory[localMatchID][puuID]['teamPosition'],
                                  sharedMatchHistory[localMatchID][puuID]['win']]
                    newMatchData[puuID] = playerInfo
                matchListBuilder.set(newMatchData, merge=True)
    print("     Number of SR matches already added from shared list --> " + str(len(matchesAlreadyAdded)))
    EXE_META_DATA['sharedSRMatchesAlreadyPresent'] = len(matchesAlreadyAdded)
    print("     Number of SR matches to be added --> " + str(len(matchesToBeAdded)))
    #EXE_META_DATA['sharedSRMatchesPushed'] = len(matchesToBeAdded)
# Update each member's individual data sets by using the data found in the shared SR
#   match list. If the match's data was already added, it is skipped
def analyze_shared_SR_match_list(squadID, puuIDList, db):
    sharedSRList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedSRMatchList') \
                .stream()
    for matchID in sharedSRList:
        if(matchID.id == "NA_TEMP"):
            return
        srMatchData = matchID.to_dict()
        if(srMatchData['readStatus'] == False):
            EXE_META_DATA['sharedSRMatchesPushed'] += 1
            print("         Pushing SR Data from --> " + matchID.id)
            for id in srMatchData:
                if(id in puuIDList):
                    champArch = get_champ_archetype(srMatchData[id][0], db)
                    champPos = srMatchData[id][4]
                    didMemberWin = srMatchData[id][5]
                    update_member_SR_data(squadID, id, champPos, champArch, didMemberWin, db)
                    currMatch = db \
                            .document(u'TheSquad/SquadID') \
                            .collection(squadID) \
                            .document(u'SharedMatchLists') \
                            .collection(u'SharedSRMatchList') \
                            .document(matchID.id)
                    currMatch.set({u'readStatus': True}, merge=True)
def update_member_SR_data(squadID, puuID, champPos, champArch, winStatus, db):
    trueChampArch = CHAMP_DATA_VALUES[champArch]
    matchesPlayedArch = "SR_matchesPlayed_" + trueChampArch
    matchesWonArch = "SR_matchesWon_" + trueChampArch
    matchesLostArch = "SR_matchesLost_" + trueChampArch
    winrateArch = "SR_winrate_" + trueChampArch

    truChampPos = POSITION_VALUES[champPos]
    matchesPlayedPos = "SR_matchesPlayed" + truChampPos
    matchesWonPos = "SR_matchesWon" + truChampPos
    matchesLostPos = "SR_matchesLost" + truChampPos
    winratePos = "SR_winrate" + truChampPos

    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
    if(winStatus == True):
        dataBuilder.update({
            matchesPlayedArch: INCREMENT,         #Increment total SR played as Arch
            matchesWonArch: INCREMENT,            #Increment total SR WON as Arch
            matchesPlayedPos: INCREMENT,          #Increment total SR played at Pos           
            matchesWonPos: INCREMENT,             #Increment total SR WON at Pos
            "SR_totalMatchesPlayed" : INCREMENT,  #Increment total SR played
            "SR_totalMatchesWon" : INCREMENT})    #Increment total SR WON
    if(winStatus == False):
        dataBuilder.update({
            matchesPlayedArch: INCREMENT,          #Increment total ARAM played as Arch
            matchesLostArch: INCREMENT,            #Increment total ARAM LOST as Arch
            matchesPlayedPos: INCREMENT,           #Increment total ARAM played at Pos           
            matchesLostPos: INCREMENT,             #Increment total ARAM LOST at Pos
            "SR_totalMatchesPlayed" : INCREMENT,   #Increment total ARAM played
            "SR_totalMatchesLost" : INCREMENT})    #Increment total ARAM LOST

    newWinrateArch = update_member_SR_winrate_arch(dataBuilder, matchesPlayedArch, matchesWonArch)
    newWinratePos = update_member_SR_winrate_pos(dataBuilder, matchesPlayedPos, matchesWonPos)
    dataBuilder.update({winrateArch: newWinrateArch,
                        winratePos: newWinratePos})
def update_member_SR_winrate_arch(dataBuilder, matchesPlayedArch, matchesWonArch):
    memberData = dataBuilder.get().to_dict()
    matchesPlayed = memberData[matchesPlayedArch]
    matchesWon = memberData[matchesWonArch]
    newWinrateArch = (matchesWon/matchesPlayed)
    newWinrateArch = round(newWinrateArch, 2)
    return newWinrateArch
def update_member_SR_winrate_pos(dataBuilder, matchesPlayedPos, matchesWonPos): 
    memberData = dataBuilder.get().to_dict()
    matchesPlayed = memberData[matchesPlayedPos]
    matchesWon = memberData[matchesWonPos]
    newWinratePos = (matchesWon/matchesPlayed)
    newWinratePos = round(newWinratePos, 2)
    return newWinratePos                     

# Can optimize in the future to pull in each member's data list then 
#   pass those into the function for management. This way, a new call
#   to pull in a member's data sheet doesn't have to occur again
#   for each type of update.
def update_squad_ARAM_data_set(squadID, puuIDList, db):
    assWRs = []
    encWRs = []
    figWRs = []
    magWRs = []
    marWRs = []
    supWRs = []
    tanWRs = []
    
    for puuID in puuIDList:
        dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
        memData = dataBuilder.get().to_dict()
        playerName = memData['summonerName']
        assWRs.append({"winrate": memData['ARAM_winrate_Assasin'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Assasin']})
        encWRs.append({"winrate": memData['ARAM_winrate_Enchanter'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Enchanter']})
        figWRs.append({"winrate": memData['ARAM_winrate_Fighter'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Fighter']})
        magWRs.append({"winrate": memData['ARAM_winrate_Mage'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Mage']})
        marWRs.append({"winrate": memData['ARAM_winrate_Marksman'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Marksman']})
        supWRs.append({"winrate": memData['ARAM_winrate_Support'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Support']})
        tanWRs.append({"winrate": memData['ARAM_winrate_Tank'],
                       "name": playerName,
                       "matchesPlayed": memData['ARAM_matchesPlayed_Tank']})

    # Sort each incoming winrate list by winrate
    assWRs = sorted(assWRs, key=itemgetter('winrate'), reverse=True)
    encWRs = sorted(encWRs, key=itemgetter('winrate'), reverse=True)
    figWRs = sorted(figWRs, key=itemgetter('winrate'), reverse=True)
    magWRs = sorted(magWRs, key=itemgetter('winrate'), reverse=True)
    marWRs = sorted(marWRs, key=itemgetter('winrate'), reverse=True)
    supWRs = sorted(supWRs, key=itemgetter('winrate'), reverse=True)
    tanWRs = sorted(tanWRs, key=itemgetter('winrate'), reverse=True)

    numMembers = len(puuIDList)
    assWRList = []
    encWRList = []
    figWRList = []
    magWRList = []
    marWRList = []
    supWRList = []
    tanWRList = []
    for i in range(numMembers):
        assWRList.append(assWRs[i]['name'])
        assWRList.append(assWRs[i]['winrate'])
        assWRList.append(assWRs[i]['matchesPlayed'])
        encWRList.append(encWRs[i]['name'])
        encWRList.append(encWRs[i]['winrate'])
        encWRList.append(encWRs[i]['matchesPlayed'])
        figWRList.append(figWRs[i]['name'])
        figWRList.append(figWRs[i]['winrate'])
        figWRList.append(figWRs[i]['matchesPlayed'])
        magWRList.append(magWRs[i]['name'])
        magWRList.append(magWRs[i]['winrate'])
        magWRList.append(magWRs[i]['matchesPlayed'])
        marWRList.append(marWRs[i]['name'])
        marWRList.append(marWRs[i]['winrate'])
        marWRList.append(marWRs[i]['matchesPlayed'])
        supWRList.append(supWRs[i]['name'])
        supWRList.append(supWRs[i]['winrate'])
        supWRList.append(supWRs[i]['matchesPlayed'])
        tanWRList.append(tanWRs[i]['name'])
        tanWRList.append(tanWRs[i]['winrate'])
        tanWRList.append(tanWRs[i]['matchesPlayed'])

    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    dataBuilder.set({u'ARAM_sqWinrates_Assasin': assWRList,
                     u'ARAM_sqWinrates_Enchanter': encWRList,
                     u'ARAM_sqWinrates_Fighter': figWRList,
                     u'ARAM_sqWinrates_Mage': magWRList,
                     u'ARAM_sqWinrates_Marksman': marWRList,
                     u'ARAM_sqWinrates_Support': supWRList,
                     u'ARAM_sqWinrates_Tank': tanWRList}, merge=False)
                    # merge=False erases everything previously
                    # merge=True simply adds to items already there
    
    update_squad_ARAM_winrate(squadID, puuIDList, db)
def update_squad_ARAM_winrate(squadID, puuIDList, db):
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuIDList[0])
    memData = dataBuilder.get().to_dict()
    # Since every member play, won, lost together, the total matches
    #   played, won, and lost can be represented by one of them
    aramTotalPlayed = memData['ARAM_totalMatchesPlayed']
    aramTotalWon = memData['ARAM_totalMatchesWon']
    aramTotalLost = memData['ARAM_totalMatchesLost']
    if(aramTotalWon == 0):
        aramWinrate = 0.00
    else:
        aramWinrate = (aramTotalWon/aramTotalPlayed)
    aramWinrate = round(aramWinrate, 2)
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    dataBuilder.set({u'ARAM_sqMatchesLost': aramTotalLost,
                     u'ARAM_sqMatchesPlayed': aramTotalPlayed,
                     u'ARAM_sqMatchesWon': aramTotalWon,
                     u'ARAM_sqWinrate': aramWinrate}, merge=True)
def update_squad_SR_data_set(squadID, puuIDList, db):
    update_squad_SR_data_set_arch(squadID, puuIDList, db)
    update_squad_SR_data_set_pos(squadID, puuIDList, db)
    update_squad_SR_winrate(squadID, puuIDList, db)
def update_squad_SR_data_set_arch(squadID, puuIDList, db):
    assWRs = []
    encWRs = []
    figWRs = []
    magWRs = []
    marWRs = []
    supWRs = []
    tanWRs = []
    for puuID in puuIDList:
        dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
        memData = dataBuilder.get().to_dict()
        playerName = memData['summonerName']
        assWRs.append({"winrate": memData['SR_winrate_Assasin'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Assasin']})
        encWRs.append({"winrate": memData['SR_winrate_Enchanter'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Enchanter']})
        figWRs.append({"winrate": memData['SR_winrate_Fighter'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Fighter']})
        magWRs.append({"winrate": memData['SR_winrate_Mage'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Mage']})
        marWRs.append({"winrate": memData['SR_winrate_Marksman'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Marksman']})
        supWRs.append({"winrate": memData['SR_winrate_Support'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Support']})
        tanWRs.append({"winrate": memData['SR_winrate_Tank'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayed_Tank']})
        
    assWRs = sorted(assWRs, key=itemgetter('winrate'), reverse=True)
    encWRs = sorted(encWRs, key=itemgetter('winrate'), reverse=True)
    figWRs = sorted(figWRs, key=itemgetter('winrate'), reverse=True)
    magWRs = sorted(magWRs, key=itemgetter('winrate'), reverse=True)
    marWRs = sorted(marWRs, key=itemgetter('winrate'), reverse=True)
    supWRs = sorted(supWRs, key=itemgetter('winrate'), reverse=True)
    tanWRs = sorted(tanWRs, key=itemgetter('winrate'), reverse=True)

    numMembers = len(puuIDList)
    assWRList = []
    encWRList = []
    figWRList = []
    magWRList = []
    marWRList = []
    supWRList = []
    tanWRList = []
    for i in range(numMembers):
        assWRList.append(assWRs[i]['name'])
        assWRList.append(assWRs[i]['winrate'])
        assWRList.append(assWRs[i]['matchesPlayed'])
        encWRList.append(encWRs[i]['name'])
        encWRList.append(encWRs[i]['winrate'])
        encWRList.append(encWRs[i]['matchesPlayed'])
        figWRList.append(figWRs[i]['name'])
        figWRList.append(figWRs[i]['winrate'])
        figWRList.append(figWRs[i]['matchesPlayed'])
        magWRList.append(magWRs[i]['name'])
        magWRList.append(magWRs[i]['winrate'])
        magWRList.append(magWRs[i]['matchesPlayed'])
        marWRList.append(marWRs[i]['name'])
        marWRList.append(marWRs[i]['winrate'])
        marWRList.append(marWRs[i]['matchesPlayed'])
        supWRList.append(supWRs[i]['name'])
        supWRList.append(supWRs[i]['winrate'])
        supWRList.append(supWRs[i]['matchesPlayed'])
        tanWRList.append(tanWRs[i]['name'])
        tanWRList.append(tanWRs[i]['winrate'])
        tanWRList.append(tanWRs[i]['matchesPlayed'])

    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    dataBuilder.set({u'SR_sqWinrates_Assasin': assWRList,
                     u'SR_sqWinrates_Enchanter': encWRList,
                     u'SR_sqWinrates_Fighter': figWRList,
                     u'SR_sqWinrates_Mage': magWRList,
                     u'SR_sqWinrates_Marksman': marWRList,
                     u'SR_sqWinrates_Support': supWRList,
                     u'SR_sqWinrates_Tank': tanWRList}, merge=True)
def update_squad_SR_data_set_pos(squadID, puuIDList, db):
    botWRs = []
    junWRs = []
    midWRs = []
    supWRs = []
    topWRs = []
    for puuID in puuIDList:
        dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuID)
        memData = dataBuilder.get().to_dict()
        playerName = memData['summonerName']
        botWRs.append({"winrate": memData['SR_winrateBot'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayedBot']})
        junWRs.append({"winrate": memData['SR_winrateJung'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayedJung']})
        midWRs.append({"winrate": memData['SR_winrateMid'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayedMid']})
        supWRs.append({"winrate": memData['SR_winrateSup'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayedSup']})
        topWRs.append({"winrate": memData['SR_winrateTop'],
                       "name": playerName,
                       "matchesPlayed": memData['SR_matchesPlayedTop']})
    botWRs = sorted(botWRs, key=itemgetter('winrate'), reverse=True)
    junWRs = sorted(junWRs, key=itemgetter('winrate'), reverse=True)
    midWRs = sorted(midWRs, key=itemgetter('winrate'), reverse=True)
    supWRs = sorted(supWRs, key=itemgetter('winrate'), reverse=True)
    topWRs = sorted(topWRs, key=itemgetter('winrate'), reverse=True)

    numMembers = len(puuIDList)
    botWRList = []
    junWRList = []
    midWRList = []
    supWRList = []
    topWRList = []
    for i in range(numMembers):
        botWRList.append(botWRs[i]['name'])
        botWRList.append(botWRs[i]['winrate'])
        botWRList.append(botWRs[i]['matchesPlayed'])
        junWRList.append(junWRs[i]['name'])
        junWRList.append(junWRs[i]['winrate'])
        junWRList.append(junWRs[i]['matchesPlayed'])
        midWRList.append(midWRs[i]['name'])
        midWRList.append(midWRs[i]['winrate'])
        midWRList.append(midWRs[i]['matchesPlayed'])
        supWRList.append(supWRs[i]['name'])
        supWRList.append(supWRs[i]['winrate'])
        supWRList.append(supWRs[i]['matchesPlayed'])
        topWRList.append(topWRs[i]['name'])
        topWRList.append(topWRs[i]['winrate'])
        topWRList.append(topWRs[i]['matchesPlayed'])


    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    dataBuilder.set({u'SR_sqWinrates_Bot': botWRList,
                     u'SR_sqWinrates_Jung': junWRList,
                     u'SR_sqWinrates_Mid': midWRList,
                     u'SR_sqWinrates_Sup': supWRList,
                     u'SR_sqWinrates_Top': topWRList}, merge=True)
def update_squad_SR_winrate(squadID, puuIDList, db):
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(puuIDList[0])
    memData = dataBuilder.get().to_dict()
    srTotalPlayed = memData['SR_totalMatchesPlayed']
    srTotalWon = memData['SR_totalMatchesWon']
    srTotalLost = memData['SR_totalMatchesLost']
    if(srTotalWon == 0):
        srWinrate = 0.00
    else:
        srWinrate = (srTotalWon/srTotalPlayed)
    srWinrate = round(srWinrate, 2)
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    dataBuilder.set({u'SR_sqMatchesLost': srTotalLost,
                     u'SR_sqMatchesPlayed': srTotalPlayed,
                     u'SR_sqMatchesWon': srTotalWon,
                     u'SR_sqWinrate': srWinrate}, merge=True)

def wrap_up(squadID, db):
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    currDate = get_current_date()
    currTime = get_current_time()
    dataBuilder.set({u'dateUpdated': currDate,
                     u'timeUpdated': currTime}, merge=True)                  

def get_champ_archetype(champName, db):
    champDataList = db.document(u'TheSquad/championData').get()
    champList = champDataList.to_dict()
    archetype = champList[champName][1]
    return archetype

def save_exe_meta_data(db):
    
    sysDate = date.today()
    currDateLog = sysDate.strftime("%m%d%Y")
    sysTime = datetime.now()
    currTimeLog = sysTime.strftime("%H%M%S")

    dataLogID = (currDateLog + "." + currTimeLog)
    dataBuilder = db.collection(u'Data').document(dataLogID)
    dataBuilder.set(EXE_META_DATA)
"""
save_squad_data_to_squad(squad, db):
- This function retrieves data from squad data stored in the database and
    converts it to a dict. It then extracts the keys from the dict and converts 
    them to a list and sorts them. 
- A new dictionary is made with the same key-value pairs but with the keys sorted.
    The squad in process is then updated with the newly calculated data.

    Parameters:
    param1 (squad obj.): The full squad object reference
    param2 (db obj.): Firestore database pointer and controller

"""
def save_squad_data_to_squad(squad, db):
    squadData = db \
            .document(u'TheSquad/SquadID') \
            .collection(squad.get_squad_id()) \
            .document(u'SquadData')
    squadDataList = squadData.get().to_dict()
    metricsList = list(squadDataList.keys())
    metricsList.sort()
    sortedDataList = {i: squadDataList[i] for i in metricsList}
    squad.set_squad_data(sortedDataList)

def is_update_necessary(squad):
    squadID = squad.get_squad_id()
    db = firestore.client()
    dataBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    sqData = dataBuilder.get().to_dict()
    dateUpdated = sqData["dateUpdated"] if "dateUpdated" in sqData else None
    timeUpdated = sqData["timeUpdated"] if "timeUpdated" in sqData else None
    if dateUpdated is None or timeUpdated is None:
        return True
    
    current_date = get_current_date()
    if dateUpdated != current_date:
        return True
    
    # If the dates are the same, compare times
    stored_time = datetime.strptime(timeUpdated, "%H:%M:%S")
    current_time = datetime.strptime(get_current_time(), "%H:%M:%S")
    time_difference = current_time - stored_time

    # Fashioned this way so the "time period" can easily be changed
    # 20 minutes is a decent standard for most League of Legends Games
    if time_difference > timedelta(minutes=20):
        return True
    else:
        save_squad_data_to_squad(squad, db)
    # ELSE
    return False

# Usage - Reset data individual member data points and readStatus of each
#         match to FALSE. This doubles as a means to cleanly add data points
#         when and if needed (except for the summonerName)
def clear_all_member_data_sets(squadID, memberInfo, db):
    # Clear member data list by setting each data point to 0
    for member in memberInfo:
        squadBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadMembers') \
                    .collection(u'MemberData') \
                    .document(member[4])
        squadBuilder.set(MEMBER_DATA)
        squadBuilder.set({u'summonerName': member[0]}, merge=True)
    
    # Clear all matches in the shared ARAM list by changing the readStatus to FALSE
    sharedARAMList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedARAMMatchList') \
                .stream()
    for matchID in sharedARAMList:
        currMatch = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedARAMMatchList') \
                .document(matchID.id)
        currMatch.set({u'readStatus': False}, merge=True)
    
    # Clear all matches in the shared ARAM list by changing the readStatus to FALSE
    sharedSRList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedSRMatchList') \
                .stream()
    for matchID in sharedSRList:
        currMatch = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedSRMatchList') \
                .document(matchID.id)
        currMatch.set({u'readStatus': False}, merge=True)
    
    squadBuilder = db \
                    .document(u'TheSquad/SquadID') \
                    .collection(squadID) \
                    .document(u'SquadData')
    squadBuilder.set(SQUAD_DATA, merge=True)

# Helper methods to sift through the stored match list and update info
def retrieve_ARAM_db_match_list(squadID):
    #Initiate Firebase session
    db = firestore.client()
    savedSquadARAMList = []
    sharedARAMList = db \
                .document(u'TheSquad/SquadID') \
                .collection(squadID) \
                .document(u'SharedMatchLists') \
                .collection(u'SharedARAMMatchList') \
                .stream()
    for matchID in sharedARAMList:
        if(matchID.id != "NA_TEMP"):
            savedSquadARAMList.append(matchID.id)
    print(savedSquadARAMList)
    return savedSquadARAMList
def ARAM_match_list_data_repair(squadID, puuIDList, repairedMatchList):
    db = firestore.client()
    for matchID in repairedMatchList:
        gameMode = repairedMatchList[matchID]['gameMode']
        gameDuration = repairedMatchList[matchID]['gameDuration']
        if (gameMode == 'ARAM'):
            matchDataBuilder = db \
                        .document(u'TheSquad/SquadID') \
                        .collection(squadID) \
                        .document(u'SharedMatchLists') \
                        .collection(u'SharedARAMMatchList') \
                        .document(matchID)
            newMatchData = {u'gameDuration' : gameDuration,
                            u'gameMode': gameMode,
                            u'readStatus': True}
            newMatchData['enemyTeam'] = repairedMatchList[matchID]['enemyTeam']
            for puuID in puuIDList:
                    newMatchData[puuID] = [repairedMatchList[matchID][puuID]['championName'], 
                                           repairedMatchList[matchID][puuID]['win']]
            matchDataBuilder.set(newMatchData, merge=True)

# 24-Hour Clock - "00:00:00"
def get_current_time():
    sysTime = datetime.now()
    currTime = sysTime.strftime("%H:%M:%S")
    return currTime
# Natural Date - "00.00.0000"
def get_current_date():
    sysDate = date.today()
    currDate = sysDate.strftime("%m.%d.%Y")
    return currDate


# Helper method to help developer add champions and their associated data
def add_champ_data():
    # Initialize connection to database
    #firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Begin user input section
    addNewChamp = True
    print("***Begin champion adding protocol***")
    while addNewChamp:
        newChamp = input('Champion Name: ')
        print("Options: [Top-> 1] [Jungle-> 2] [Mid-> 3] [Bottom-> 4] [Support-> 5] ")
        mostCommonPosition = int(input('Most Common Position: '))
        print("Options: [Assasin-> 6] [Fighter-> 7] [Mage-> 8]\n"
              "         [Marksman-> 9] [Support-> 10] [Tank-> 11]")
        primaryChampRole = int(input('Primary Role: '))
        print("Options: [Assasin-> 6] [Fighter-> 7] [Mage-> 8]\n"
              "         [Marksman-> 9] [Support-> 10] [Tank-> 11]\n"
              "         [Enchanter-> 12] [Juggernaut-> 13] [Crowd Control-> 14]")
        secondaryChampRole = int(input('Secondary Role: '))
        champRef = db.collection(u'TheSquad').document(u'championData')
        champRef.set({
            newChamp: [mostCommonPosition, primaryChampRole, secondaryChampRole]
        }, merge=True)
        continueCheck = input("Continue? (y/n): ")
        if continueCheck != 'y':
            addNewChamp = False