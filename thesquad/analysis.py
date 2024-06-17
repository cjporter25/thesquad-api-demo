import math
from scipy.stats import norm
from scipy.stats import ttest_1samp
from pprint import pprint

CONFIDENCE_LEVEL_LOW = 0.90
CONFIDENCE_LEVEL_STAN = 0.95
CONFIDENCE_LEVEL_HIGH = 0.99
Z_SCORE_LOW = norm.ppf((1 + CONFIDENCE_LEVEL_LOW)/2)
Z_SCORE_STAN = norm.ppf((1 + CONFIDENCE_LEVEL_STAN)/2)
Z_SCORE_HIGH = norm.ppf((1 + CONFIDENCE_LEVEL_HIGH)/2)

ARCHETYPES_ARAM = ["Assasin", 
                   "Enchanter", 
                   "Fighter", 
                   "Mage", 
                   "Marksman",
                   "Tank"]

ARCHETYPE_KEYS = ["ARAM_sqWinrates_Assasin", 
                  "ARAM_sqWinrates_Enchanter", 
                  "ARAM_sqWinrates_Fighter", 
                  "ARAM_sqWinrates_Mage", 
                  "ARAM_sqWinrates_Marksman", 
                  "ARAM_sqWinrates_Tank"]

SQUAD_STATS = {"Assasin": {},
               "Enchanter": {}, 
               "Fighter": {}, 
               "Mage": {}, 
               "Marksman": {},
               "Tank": {}}
def conduct_squad_analysis(squadData):
    initialResults = calculate_squad_stats(squadData)
    # pprint(initialResults)
    normalizedResults = normalize_squad_stats(initialResults)
    # pprint(normalizedResults)
    finalResults = finalize_squad_stats(normalizedResults)
    pprint(finalResults)

# "Archetype_winrate": [player1, winrate, gamesplayed, 
#                       player2, winrate, gamesplayed, 
#                       player3, winrate, gamesplayed]
def calculate_squad_stats(squadData):
    sqWinrate = squadData["ARAM_sqWinrate"]
    sqMatchesPlayed = squadData["ARAM_sqMatchesPlayed"]
    squadStats = SQUAD_STATS
    for archetype in ARCHETYPES_ARAM:
        players = []
        print("Comparing " + archetype + ".......")
        key = "ARAM_sqWinrates_" + archetype
        playerArchData = squadData[key]
    # Unforunate requirement to parse data in an efficient manner due to how
    #   the data is stored in firebase
    # Range = size of incoming list. Index starts at 0 and moves up three spaces
    #         each loop iteration.
    # The name, winrate, and gamesplayed of each player is then pulled, analyzed
    #       and saved.
        for i in range(0, len(playerArchData), 3):
            playerName = playerArchData[i]
            winrate = playerArchData[i+1]
            matchesPlayed = playerArchData[i+2]
            ci = calculate_wilson_score_interval(winrate, matchesPlayed, 
                                                 CONFIDENCE_LEVEL_STAN)
            player = {"name": playerName,
                    "memWinrate": winrate,
                    "matchesPlayedAs": matchesPlayed,
                    "adjustedMemWinrate": adjusted_winrate(winrate, 
                                                           sqWinrate),
                    "contribution": member_contribution(winrate, 
                                                        matchesPlayed, 
                                                        sqMatchesPlayed),
                    "ci": [ci[0], ci[1]],
                    "ciWidth": ci[2]}
            players.append(player)
            squadStats[archetype] = players
    return squadStats

def normalize_squad_stats(squadStats):
    for archetype in ARCHETYPES_ARAM:
        max_matches = max(player["matchesPlayedAs"] for player in squadStats[archetype])
        max_contribution = max(player["contribution"] for player in squadStats[archetype])
        min_lb_ci = min(player["ci"][0] for player in squadStats[archetype])
        max_lb_ci = max(player["ci"][0] for player in squadStats[archetype])
        min_ci_width = min(player["ciWidth"] for player in squadStats[archetype])
        max_ci_width = max(player["ciWidth"] for player in squadStats[archetype])
        for player in squadStats[archetype]:
            player["norm_games"] = normalize(player["matchesPlayedAs"], 0, max_matches)
            player["norm_contribution"] = normalize(player["contribution"], 0, max_contribution)
            player["norm_ci"] = normalize(player["ci"][0], min_lb_ci, max_lb_ci)
            player["norm_ci_width"] = normalize(player["ciWidth"], min_ci_width, max_ci_width)
            player["combined_score"] = round((0.30 * player["norm_ci"] +
                                        0.30 * (1.00 - player["norm_ci_width"]) +  # Prefer narrower intervals
                                        0.20 * player["adjustedMemWinrate"] +
                                        0.20 * player["norm_contribution"]), 2)
    return squadStats

def finalize_squad_stats(squadStats):
    results = []
    for archetype in ARCHETYPES_ARAM:
        best_player = max(squadStats[archetype], key=lambda x: x["combined_score"])
        results.append({
            "archetype": archetype,
            "best_player": best_player["name"],
            "combined_score": best_player["combined_score"]
        })
    for result in results:
        print(f"The best player for the '{result['archetype']}'archetype is {result['best_player']} with a combined score of {result['combined_score']:.4f}")

# Normalize function
def normalize(value, min_value, max_value):
    if max_value - min_value == 0:
        return 0
    return round(((value - min_value) / (max_value - min_value)), 2)



# Adjusting each player's win rate by comparing it the squad's overall win rate
def adjusted_winrate(memberWinrate, squadWinrate):
    return round((memberWinrate - squadWinrate), 2)

# Calculate the contribution of each player's performance to the overall squad winrate.
# Num of games played vs. total matches played by the squad
def member_contribution(memberWinrate, matchesPlayedAs, totalSquadMatches):
    return round(((memberWinrate * matchesPlayedAs) / totalSquadMatches), 4)

# Conduct a significance test to compare the member's wr with the squad's wr
def significance_test(memberWinrate, squadWinrate):
    #t_stat uneeded but has to be assisgned
    t_stat, p_value = ttest_1samp(memberWinrate, squadWinrate)
    return p_value

def calculate_wilson_score_interval(winrate, games, confidenceLevel):
    if games == 0:
        return [0, 0, 0] # No games played as that type
    z = norm.ppf((1 + confidenceLevel) / 2)
    p = winrate
    n = games
    denominator = 1 + z**2 / n
    cap = p + z**2 / (2 * n)
    adjustedStandardDeviation = math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    lowerBound = round(((cap - z * adjustedStandardDeviation) / denominator), 2)
    upperBound = round(((cap + z * adjustedStandardDeviation) / denominator), 2)
    intervalSize = round((upperBound - lowerBound), 2)

    return [lowerBound, upperBound, intervalSize]

def calculate_confidence_interval(winrate, games, confidenceLevel):
    # Calculate z-score
    zScore = norm.ppf((1 + confidenceLevel)/2)

    # STANDARD ERROR: Measures the variability of the win rate estimate
    se = math.sqrt(winrate * (1 - winrate) / games)
    # Calcualte margin of error or (z-score * standard error)
    marginOfError = zScore * se
    # Find the lower bound of interval
    lowerBound = winrate - marginOfError
    # Find the higher bound of interval
    higherBound = winrate + marginOfError
    return lowerBound, higherBound


