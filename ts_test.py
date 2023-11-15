import sys

# Only works because there is an "__init__.py" file inside that directory.
#   Python then interprets the folder as a python package.
from app_util import *
import unittest

#TEST
#   Check whether summoner name exists
#       Attempt account info retrieval. If Riot API response is a bad code,
#       Tell user that the name wasn't valid.
#   Check whether stored match lists are the correct gameMode type
#       Sift through a given squad's shared match histories. Call upon
#       the Riot API using the MatchID, cross reference the matches game
#       mode with what is expected.
#   Check that all squadID's have the correct character lengths
#       Pull in the list of currently stored ID's and check that the
#       number of characters is a multiple of 4, and is consistent with the
#       expected "size" of the squad.
#   Test timing required to create a new squad or update one
#       Establish a timer, create squad, stop timer once firebase completes
#       scaffolding or checking through what needs to change.
#       Create a theoretical "set" of data to input as a Full member squad with
#       10 shared ARAM and 10 shared SR matches
#   Run through every squadID for format consistency
#       Establish a known good and known bad squad ID (with various aspects not
#       formatted correctly) Ensure the test reports the errors back correctly.
#       Idea - Build components that check specific elements, similar to the building
#       algorithm, and then call all of them under one umbrella.

##### WARNING WARNING WARNING - REMOVE THIS BEFORE PUSHING TO HEROKU #####
KGmatchID = "NA1_4789688057"
KGpuuID = "k6JM2AMfEJlM9SXmsDSzlc1YM96OzSut42yR1E7XkDTjynBkbdyBO6uAzlLAJjX6fhMg2X6cDKOFxQ"
KGsquadID = "8I_GBKGGSh_t_aJU"

def test_user_input():
    test1 = is_mem_list_valid(NON_VALID_MEM_LIST_1)
    test2 = is_mem_list_valid(VALID_MEM_LIST_2)
    test3 = is_mem_list_valid(VALID_MEM_LIST_3)
    test4 = is_mem_list_valid(VALID_MEM_LIST_4)
    test5 = is_mem_list_valid(VALID_MEM_LIST_5)
    test6 = is_mem_list_valid(NON_VALID_MEM_LIST_6)
    testShortName = is_mem_name_valid(KB_SHORT_NAME)
    testLongName = is_mem_name_valid(KB_TOO_LONG_NAME)
    testGoodListShortName = is_mem_list_valid(KB_GOOD_LIST_SHORT_NAME)
    testGoodListLongName = is_mem_list_valid(KB_GOOD_LIST_LONG_NAME)
    assert test1 == False, "Incorrect List"
    assert test2 == True, "Incorrect List"
    assert test3 == True, "Incorrect List"
    assert test4 == True, "Incorrect List"
    assert test5 == True, "Incorrect List"
    assert test6 == False, "Incorrect List"
    assert testShortName == False, "Incorrect Name"
    assert testLongName == False, "Incorrect Name"
    assert testGoodListShortName == False, "Incorrect List"
    assert testGoodListLongName == False, "Incorrect List"
#{
#    "status": {
#        "message": "Unauthorized",
#        "status_code": 401,
#    }
#}

def test_response_codes(APIKEY):
    test_response_success(APIKEY)
    test_response_badrequest(APIKEY)
    test_response_unathorized()
    test_response_forbidden()
    test_response_not_found(APIKEY)
    test_response_unsupported_media_type(APIKEY)

# Anything successful is guaranteed to return a JSON response body. Affirm that
    #   the incoming status_code from the request object for a call to a known 
    #   good summoner name: Chrispychickn25
    # Usage - Make a call to retrieve player info. Expects the correct URL, a 
    #        summoner name, and api key. Using a KG summoner name should result in
    #        a success response code.
def test_response_success(APIKEY):
    print("Test Request - Successful")
    response = test_get_player_info(KG_PLAYER_NAME, APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_SUCCESS))
    print("     Actual: " + str(response.status_code))
    assert response.status_code == RESPONSE_CODE_SUCCESS, "Unexpected Code"

# Code - "Bad Request". Indicates a syntax error in the request and
    #   it is therefore denied. Common reasons -> wrong parameter type, 
    #   parameter value is invalid, parameter was not divided
    # Usage - Make a call to retrieve match history. Expects the correct URL, player
    #        puuID, and api key. Using an acctID rather than a puuID should result in 
    #        the specific response code
def test_response_badrequest(APIKEY):
    print("Test Request - Bad Request")
    response = get_match_history(KG_ACCTID, DEF_MATCH_HISTORY_COUNT, APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_BADREQUEST))
    print("     Actual: " + str(response['status']["status_code"]))
    assert response['status']["status_code"] == RESPONSE_CODE_BADREQUEST, "Unexpected Code"

# Code - "Unathorized". Indicates that the request being made did not
    #   contain the necessary authentication credentials, i.e., apikey was not
    #   provided.
    # Usage - Make a call to retrieve match data. Expects the correct URL, 
    #         matchID, and a valid apikey. Not providing an API key should
    #         trigger the specific response code.
def test_response_unathorized():
    print("Test Request - Unauthorized")
    response = get_match(KG_MATCHID, KB_EMPTY_APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_UNAUTHORIZED))
    print("     Actual: " + str(response['status']["status_code"]))
    assert response['status']["status_code"] == RESPONSE_CODE_UNAUTHORIZED, "Unexpected Code"

# Code - "Forbidden". Indicates that the request being made could not be
    #   authorized. Usually due to invalid API key, blacklisted API key, or 
    #   request was for an incorrect path.
    # Usage - Make a call to retrieve match data. Expects the correct URL, matchID,
    #         and a valid apikey. Providing a bad apikey, should trigger the specific response
def test_response_forbidden():
    print("Test Request - Forbidden")
    response = get_match(KG_MATCHID, KB_SHORT_APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_FORBIDDEN))
    print("     Actual: " + str(response['status']["status_code"]))
    assert response['status']["status_code"] == RESPONSE_CODE_FORBIDDEN, "Unexpected Code"


# Code - "Not Found". Indicates that the request being made could not find
    #   a match to the input resource, i.e., summoner name, matchID, etc.
    # Usage - Make a call to retrieve a players information. Expects the correct URL,
    #         a valid summoner name, and a valid apikey. Providing a known non-existent
    #         player name should trigger the specific response
def test_response_not_found(APIKEY):
    print("Test Request - Not Found")
    response = test_get_player_info(KB_PLAYER_NAME, APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_NOTFOUND))
    print("     Actual: " + str(response.status_code))
    assert response.status_code == RESPONSE_CODE_NOTFOUND, "Unexpected Code"

# Code - "Unsupported Media Type". Usually indicates a non-supported
    #   body format, i.e., the content ID and apikey are correct but the
    #   URL format is not matched correctly with what's expected.
    # Usage - Make a call to retrieve match data. Expects the correct URL,
    #         a valid matchID, and a valid apikey. Using a KB URL, which will 
    #         hard coded into a test variant of "get_match", should trigger the
    #         specific response.
def test_response_unsupported_media_type(APIKEY):
    print("Test Request - Unsupported Media Type")
    response = test_get_match(KG_MATCHID, APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_UNSUPPORTED_MEDIA_TYPE) + " or " + \
                              str(RESPONSE_CODE_FORBIDDEN))
    print("     Actual: " + str(response.status_code))
    assert response.status_code == RESPONSE_CODE_UNSUPPORTED_MEDIA_TYPE or \
                                   RESPONSE_CODE_FORBIDDEN, "Unexpected Code"

# Code - "Rate Limit Exceeded". Indicates that one or more of the
    #   allotted request limit amounts was exceeded. There is a rate 
    #   limit for number of requests per second and amount of requests 
    #   total every 2 minutes
    # Usage - Make a series of requests, totaling the max for the 2 minutes.
    #         pausing briefly every so often so that the short term doesn't trigger.
    #         The goal is to see that a request made after the max was reached 
    #         in fact returns the specific code.
def test_response_rate_limit_exceeded(APIKEY):
    print("Test Request - Rate Limit Exceeded")
    for count in range(RATE_LIMIT_LOOP_COUNT):
        for matchID in KG_MATCH_ID_LIST_20:
            response = get_match(matchID, APIKEY)
        Event().wait(1)
        print("Testing Rate Limit...")
    response = test_get_match(KG_MATCHID, APIKEY)
    print("     Expected: " + str(RESPONSE_CODE_RATE_LIMIT_EXCEEDED))
    print("     Actual: " + str(response['status']["status_code"]))
    assert response['status']["status_code"] == RESPONSE_CODE_RATE_LIMIT_EXCEEDED, "Unexpected Code"


def test_get_match(matchID, apiKey):
    api_url_matchId = "https://americas.api.riotgames.com/lol/match/v5/match" + matchID
    api_urlkey = api_url_matchId + '?api_key=' + apiKey
    reqResp = requests.get(api_urlkey)
    return reqResp
def test_get_player_info(summonerName, apiKey):
    api_url_summName = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName
    api_urlkey = api_url_summName + '?api_key=' + apiKey
    reqResp = requests.get(api_urlkey)
    return reqResp
