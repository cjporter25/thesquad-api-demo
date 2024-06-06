import math
from scipy.stats import norm
from scipy.stats import ttest_1samp

CONFIDENCE_LEVEL_LOW = 0.90
CONFIDENCE_LEVEL_STAN = 0.95
CONFIDENCE_LEVEL_HIGH = 0.99
Z_SCORE_LOW = norm.ppf((1 + CONFIDENCE_LEVEL_LOW)/2)
Z_SCORE_STAN = norm.ppf((1 + CONFIDENCE_LEVEL_STAN)/2)
Z_SCORE_HIGH = norm.ppf((1 + CONFIDENCE_LEVEL_HIGH)/2)

# "Archetype_winrate": [player1, winrate, gamesplayed, 
#                       player2, winrate, gamesplayed, 
#                       player3, winrate, gamesplayed]
def statistically_significant_winrates(squadData):
    archetypes = ["ARAM_sqWinrates_Assasin", 
                  "ARAM_sqWinrates_Enchanter", 
                  "ARAM_sqWinrates_Fighter", 
                  "ARAM_sqWinrates_Mage", 
                  "ARAM_sqWinrates_Marksman", 
                  "ARAM_sqWinrates_Tank"]
    sqWinrate = squadData["ARAM_sqWinrate"]
    sqMatchesPlayed = squadData["ARAM_sqMatchesPlayed"]
    for key in archetypes:
        playerData = squadData[key]
        players = []
    # Unforunate requirement to parse data in an efficient manner due to how
    #   the data is stored in firebase
    # Range = size of incoming list. Index starts at 0 and moves up three spaces
    #         each loop iteration.
    # The name, winrate, and gamesplayed of each player is then pulled, a confidence
    #   interval is calculated, and this information is saved.
        for i in range(0, len(playerData), 3):
            winrate = playerData[i+1]
            matchesPlayed = playerData[i+2]
            player = {
                "name": playerData[i],
                "winrate": winrate,
                "matchesPlayedAs": matchesPlayed,
                "adjusted_winrate": adjusted_winrate(winrate, sqWinrate),
                "contribution": member_contribution(winrate, matchesPlayed, sqMatchesPlayed),
                "p_value": significance_test(winrate, sqWinrate),
                "ci": calculate_wilson_score_interval(winrate, matchesPlayed, 
                                                      CONFIDENCE_LEVEL_STAN)
            }
            players.append(player)

        # Determine the best player based on the highest lower bound of the confidence interval

# Adjusting each player's win rate by comparing it the squad's overall win rate
def adjusted_winrate(memberWinrate, squadWinrate):
    return memberWinrate - squadWinrate

# Calculate the contribution of each player's performance to the overall squad winrate.
# Num of games played vs. total matches played by the squad
def member_contribution(memberWinrate, matchesPlayedAs, totalSquadMatches):
    return (memberWinrate * matchesPlayedAs) / totalSquadMatches

# Conduct a significance test to compare the member's wr with the squad's wr
def significance_test(memberWinrate, squadWinrate):
    #t_stat uneeded but has to be assisgned
    t_stat, p_value = ttest_1samp(memberWinrate, squadWinrate)
    return p_value



def calculate_wilson_score_interval(winrate, games, confidenceLevel):
    if games == 0:
        return 0, 0 # No games played as that type
    z = norm.ppf((1 + confidenceLevel) / 2)
    p = winrate
    n = games
    denominator = 1 + z**2 / n
    cap = p + z**2 / (2 * n)
    adjustedStandardDeviation = math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    lowerBound = (cap - z * adjustedStandardDeviation) / denominator
    upperBound = (cap + z * adjustedStandardDeviation) / denominator

    return [lowerBound, upperBound]

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


