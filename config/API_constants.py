RATE_LIMIT_EXCEEDED = 429
BODY_JSON_RESPONSE = 200

FETCHED_PARTICIPANT_MATCHES = 10

SEMAPHORE_LIMIT = 2

DISCORD_RATE_LIMIT_TIMEOUT = 5

RANKED_SOLO_DUO = 420

# Map common region codes to platform routing values needed by Riot API
# and regional endpoints.
REGION_TO_PLATFORM = {
    "NA": "na1",
    "EUW": "euw1",
    "EUNE": "eun1",
    "KR": "kr",
    "JP": "jp1",
    "BR": "br1",
    "OCE": "oc1",
    "LAN": "la1",
    "LAS": "la2",
    "RU": "ru",
    "TR": "tr1",
}

REGION_TO_REGIONAL = {
    "NA": "americas",
    "EUW": "europe",
    "EUNE": "europe",
    "KR": "asia",
    "JP": "asia",
    "BR": "americas",
    "OCE": "sea",
    "LAN": "americas",
    "LAS": "americas",
    "RU": "europe",
    "TR": "europe",
}