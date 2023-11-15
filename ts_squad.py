# Squad object Class
#   About: Contains all data structure necessary to scaffold new squad
#           information, add to what's already there, or analyze data
from ts_riot_api import *
from ts_firebase import *

import time
import json

class Squad:
    # Intializer used for testing a fully pre-built test squad object
    def __init__(self, memberList, memberInfo, 
                 squadID, apiKey, squadMatchHistory, 
                 sharedMatchHistory, squadData):
        self.memberList = memberList
        self.memberInfo = memberInfo
        self.squadID = squadID
        self._apikey = apiKey
        self.squadMatchHistory = squadMatchHistory
        self.sharedMatchHistory = sharedMatchHistory
        self.squadData = squadData
    # Initializer to build a squad when a member list and API key are given
    def __init__(self, memberList, apiKey):
        self.memberList = memberList
        self.memberInfo = []
        self.squadID = ""
        self._apikey = apiKey
        self.squadMatchHistory = []
        self.sharedMatchHistory = {}
        self.squadData = {}
    # Default initializer
    def __init__(self):
        self.memberList = []
        self.memberInfo = []
        self.squadID = ""
        self._apiKey = ""
        self.squadMatchHistory = []
        self.sharedMatchHistory = {}
        self.riotRequestCount = 0
        self.squadData = {}
    
    def initialize(self, memberList, matchHistoryCount, apiKey):
        projStart = time.time()
        squadStart = time.time()
        # init_firebase()
        # apiKey = get_riot_api_key()
        self.set_member_list(memberList)
        #self.show_member_list()
        self.gather_squad_member_info(apiKey)
        self.create_squad_id()
        #self.show_squad_ID()
            #MIN_MATCH_HISTORY_COUNT = "0"
            #REC_MATCH_HISTORY_COUNT = "90"
            #MAX_MATCH_HISTORY_COUNT = "100"
            #DEF_MATCH_HISTORY_COUNT = "20"
        self.gather_squad_match_history(matchHistoryCount, apiKey)
        self.find_shared_matches(apiKey)
        squadEnd = time.time()
        totalSquadTime = round((squadEnd - squadStart), 2)
        self.show_shared_match_history()
        self.show_request_count()
        EXE_META_DATA['exeTimeSquad'] = totalSquadTime
        print("***Squad Look-up Was Successful***")

        build_squad(self, projStart)
        #self.show_squad_data()

        data = json.dumps(EXE_META_DATA, indent=3)
        print(data)

    # Set the member variable "memberList" to equal an incoming list of strings
    def save_squad_member_list(self, newMemberList):
        self.set_member_list(newMemberList)
    # Sets the sqaud's member info list to a list of lists object where each unique ID
    #   obtained from riot is stored in a specific order. See get_player_info for order.
    def gather_squad_member_info(self, apiKey):
        print("Gathering member information...")
        newMemberInfo = []
        count = 0
        for member in self.get_member_list():
            newMemberInfo.append(get_player_info(member, apiKey))
            count = count + 1
        self.set_riot_request_count(self.get_riot_request_count() + count) #Increment count
        self.set_member_info(newMemberInfo)
        EXE_META_DATA['numMembers'] = self.get_squad_size()
        EXE_META_DATA['memDataReqCount'] = count
    def create_squad_id(self):
        tempSquadID = []

        for member in self.get_member_info():
            # Obtain current player's acctId. Located at second index
            #   acctID is a long string variable
            acctID = member[1]
            # Obtain first 4 characters of account ID string and combine them
            #   into a new four character string
            idChunk = acctID[0] + acctID[1] + acctID[2] + acctID[3]
            # Add a 4 character string to the back of the current array
            tempSquadID.append(idChunk)
            # Sort the array so the lowest level strings will always show up first
            tempSquadID.sort()
            # The result should look like --> ["asdf", "hjkl", "qwer", "uiop"]
            
            newSquadID = ""
            for chunk in tempSquadID:
                # Append each chunk as another portion of the squadID string
                newSquadID = newSquadID + chunk
        self.set_squad_id(newSquadID)
    # Sets the squad's match history list to a list of lists object where each 1st dimension 
    #   index is specific to each player and each 2nd dimension array contains their match history
    def gather_squad_match_history(self, reqAmount, apiKey):
        print("Gathering match histories...")
        newMatchHistory = []
        count = 0
        for member in self.get_member_info():
            newMatchHistory.append(get_match_history(member[4], reqAmount, apiKey))
            count = count + 1
        self.set_riot_request_count(self.get_riot_request_count() + count) #Increment count   
        self.set_squad_match_history(newMatchHistory)
        EXE_META_DATA['matchHistoryQuerySize'] = int(reqAmount)
        EXE_META_DATA['memMatchHistoryReqCount'] = count
    # Parses through the various match histories and builds a new list containing only 
    #   the matchID's where every member is present. Each match's data set, from this
    #   shared list, is then retrieve and organized in a strict format.
    def find_shared_matches(self, apiKey):
        print("Finding shared matches...")
        newSharedMatchList = {}
        squadMatchHistory = self.get_squad_match_history()
        numOfMembers = len(squadMatchHistory)
        # Used first match history in the list as a reference list to compare against the others
        for matchID in squadMatchHistory[0]:
            wholeSquadPresent = True
            for index in range(1, numOfMembers):
                if(matchID not in squadMatchHistory[index]):
                    wholeSquadPresent = False
            # If every squad member was present in this match
            if (wholeSquadPresent == True):
                match_stuff = get_match(matchID, apiKey)
                self.set_riot_request_count(self.get_riot_request_count() + 1) #Increment count
                # Save specific match's info
                matchInfo = match_stuff['info']
                # Save specific match's metadata
                matchMetadata = match_stuff['metadata']
                # Pull match data that applies to all players, i.e., game duration and mode
                newMatchData = {'gameDuration' : matchInfo['gameDuration'],
                                'gameMode' : matchInfo['gameMode'],
                                }
                # Add specific match data per squad member, based on their puuID
                for puuID in self.retrieve_puuID_list():
                    # Use indexing to find the specified members data for this match
                    playerMatchInfo = get_player_match_info(matchInfo, matchMetadata, puuID)
                    # Add a new dictionary object as the value for the puuID being added
                    newMatchData[puuID] = {'championName' : playerMatchInfo['championName'],
                                           'individualPosition' : playerMatchInfo['individualPosition'],
                                           'lane' : playerMatchInfo['lane'],
                                           'role' : playerMatchInfo['role'],
                                           'teamPosition' : playerMatchInfo['teamPosition'],
                                           'win' : playerMatchInfo['win']}
                # Save newly gathered info about the current shared match
                newSharedMatchList[matchID] = newMatchData
        # Save match
        self.set_shared_match_history(newSharedMatchList)
        EXE_META_DATA['totalRiotReqCount'] = self.get_riot_request_count()

    def EXP_find_shared_matches(self, apiKey):
        # STEP 1 - Find a list of shared matches between the 1st and 2nd Squad Members. This is
        #          the base list to compare further squad members if there are any.
        #        - In other words, if the match in question does not exist
        sharedMatchList = []
        tempList = []
        squadMatchHistory = self.get_squad_match_history()
        numOfMembers = len(squadMatchHistory)
        print("Checkpoint 1")
        for matchID in squadMatchHistory[0]:
            if(matchID in squadMatchHistory[1]):
                sharedMatchList.append(matchID)
        if numOfMembers >= 3:
            print("Checkpoint 2")
            for matchID in squadMatchHistory[2]:
                if(matchID in sharedMatchList):
                    tempList.append(matchID)
            sharedMatchList = tempList.copy()
        if numOfMembers >= 4:
            print("Checkpoint 3")
            tempList = []
            for matchID in squadMatchHistory[3]:
                if(matchID in sharedMatchList):
                    tempList.append(matchID)
            sharedMatchList = tempList.copy()
        if numOfMembers == 5:
            print("Checkpoint 4")
            tempList = []
            for matchID in squadMatchHistory[4]:
                if(matchID in sharedMatchList):
                    tempList.append(matchID)
            sharedMatchList = tempList.copy()
        
        print(sharedMatchList)
        
        sharedMatchData = {}
        # If list is not empty, actually pull in match data
        if sharedMatchList:
            print("Checkpoint 4")
            for matchID in sharedMatchList:
                match_stuff = get_match(matchID, apiKey)
                self.set_riot_request_count(self.get_riot_request_count() + 1) #Increment count

                matchInfo = match_stuff['info']
                matchMetaData = match_stuff['metadata']

                newMatchData = {'gameDuration' : matchInfo['gameDuration'],
                                'gameMode' : matchInfo['gameMode'],
                                }
                for puuID in self.retrieve_puuID_list():
                    # Use indexing to find the specified members data for this match
                    playerMatchInfo = get_player_match_info(matchInfo, matchMetaData, puuID)
                    # Add a new dictionary object as the value for the puuID being added
                    newMatchData[puuID] = {'championName' : playerMatchInfo['championName'],
                                           'individualPosition' : playerMatchInfo['individualPosition'],
                                           'lane' : playerMatchInfo['lane'],
                                           'role' : playerMatchInfo['role'],
                                           'teamPosition' : playerMatchInfo['teamPosition'],
                                           'win' : playerMatchInfo['win']}
                    sharedMatchData[matchID] = newMatchData
            self.set_shared_match_history(sharedMatchData)
            EXE_META_DATA['totalRiotReqCount'] = self.get_riot_request_count()
    
    def save_exe_meta_data(self, db):
        sysDate = date.today()
        currDateLog = sysDate.strftime("%m%d%Y")
        sysTime = datetime.now()
        currTimeLog = sysTime.strftime("%H%M%S")

        dataLogID = (currDateLog + "." + currTimeLog)
        dataBuilder = db.collection(u'Data').document(dataLogID)
        dataBuilder.set(EXE_META_DATA)
    # Calculates and returns the length of the member list which 
    #   indicates the size of the squad
    def get_squad_size(self):
        return len(self.get_member_list())

    # Parses through the member info list, retrieves each member's puuID,
    #   builds a list of these ID's, and returns the list
    def retrieve_puuID_list(self):
        puuIDList = []
        for member in self.get_member_info():
            puuIDList.append(member[4])
        puuIDList.sort()
        return puuIDList
    #####Member Variable Console Output#####
    def show_squad_info(self):
        print("****Squad Member Info****")
        print("| Members in squad -->")
        print(self.get_member_list())
        #print("| SquadID: " + self.get_squad_id() + "\n")
        
        for member in self.get_member_info():
            print("/")
            print("|Name: " + member[0])
            print("| acctID: " + member[1])
            print("| ID: " + member[2])
            print("| Level: " + member[3])
            print("| puuID: " + member[4])
            print("\\")
    def show_match_history(self):
        # Algorithm to display nicely needs work
        # May need to build a string that adds based on number
        #   of players. Once string is built, then print it
        smh = self.get_match_history()
        numOfMembers = len(smh)
        for i in range(0, 19):
            for j in range(0, numOfMembers-1):
                print(smh[j][i])
    def show_shared_match_history(self):
        totalARAM = 0
        totalSR = 0
        totalShared = 0
        sharedList = self.get_shared_match_history()
        print("        ***Shared Match History***")
        print("         -----------------------")
        for match in sharedList:
            print("         |" + match + "-->" + sharedList[match]['gameMode'] + "|")
            totalShared = totalShared + 1
            if(sharedList[match]['gameMode'] == 'ARAM'):
                totalARAM = totalARAM + 1
            if(sharedList[match]['gameMode'] == 'CLASSIC'):
                totalSR = totalSR + 1
        print("         -----------------------")
        print("             Total ARAM: " + str(totalARAM))
        EXE_META_DATA['totalSharedARAMMatches'] = totalARAM
        print("             Total SR: " + str(totalSR))
        EXE_META_DATA['totalSharedSRMatches'] = totalSR
        print("             Total Shared: " + str(totalShared))
        EXE_META_DATA['totalSharedMatches'] = totalShared      
    def show_member_list(self):
        print("     SQUAD MEMBERS -->")
        for member in self.get_member_list():
            print("          " + member) 
    def show_squad_ID(self):
        print("     Squad ID ->")
        print("          " + self.get_squad_id())
    def show_request_count(self):
        print("Validating Riot API Request Count...")
        sharedMatchListSize = len(self.get_shared_match_history())
        squadSize = self.get_squad_size()
        currCount = self.get_riot_request_count()
        print("             Total Shared: " + str(sharedMatchListSize))
        print("             Member Count: " + str(squadSize))
        print("             Request Count: " + str(currCount))
        print("             Request Count (should) = Total Shared + (Member Count * 2)")
        Event().wait(1)
    def show_squad_data(self):
        squadData = self.get_squad_data()
        for metric in squadData:
            print(metric)
            print("     --> " + str(squadData[metric]))

    #####Member variable accessor methods#####
    def get_member_list(self):
        return self.memberList
    def set_member_list(self, newMemberList):
        self.memberList = newMemberList
    def get_member_info(self):
        return self.memberInfo
    def set_member_info(self, newMemberInfo):
        self.memberInfo = newMemberInfo
    def get_squad_id(self):
        return self.squadID
    def set_squad_id(self, newSquadID):
        self.squadID = newSquadID
    def get_api_key(self):
        return self._apiKey
    def set_api_key(self, apiKey):
        self._apiKey = apiKey
    def get_squad_match_history(self):
        return self.matchHistory
    def set_squad_match_history(self, newMatchHistory):
        self.matchHistory = newMatchHistory
    def get_shared_match_history(self):
        return self.sharedMatchHistory
    def set_shared_match_history(self, newSharedMatchHistory):
        self.sharedMatchHistory = newSharedMatchHistory
    def get_riot_request_count(self):
        return self.riotRequestCount
    def set_riot_request_count(self, newRequestCount):
        self.riotRequestCount = newRequestCount
    def get_squad_data(self):
        return self.squadData
    def set_squad_data(self, newSquadData):
        self.squadData = newSquadData

