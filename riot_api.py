import os
import requests
from dotenv import load_dotenv
from time import sleep

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# Map common region codes to platform routing values needed by Riot API
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

def get_platform_and_regional(region: str):
    platform = REGION_TO_PLATFORM[region.upper()]  # → "euw1"
    regional = REGION_TO_REGIONAL[region.upper()]  # → "europe"
    if not platform or not regional:
        raise ValueError(f"Unsupported region '{region}'. Supported: {list(REGION_TO_PLATFORM.keys())}")

    return platform, regional

def get_summoner_info(summoner_name: str, tag_line: str, region: str):
    platform, regional = get_platform_and_regional(region)

    url = f"https://{regional}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting 10 seconds...")
        sleep(10)
        return get_summoner_info(summoner_name, tag_line, region)
    else:
        response.raise_for_status()

# PUUID = Platform Unique User Identifier
def get_recent_match_ids(puuid: str, region: str, count=10):
    platform, regional = get_platform_and_regional(region)

    url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"count": count}
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting 10 seconds...")
        sleep(10)
        return get_recent_match_ids(puuid, region, count)
    else:
        response.raise_for_status()

def get_match_details(match_id: str, region: str):
    platform, regional = get_platform_and_regional(region)

    url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting 10 seconds...")
        sleep(10)
        return get_match_details(match_id, region)
    else:
        response.raise_for_status()

def get_summoner_info_from_puuid(puuid: str, region: str):
    platform, regional = get_platform_and_regional(region)
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting 10 seconds...")
        sleep(10)
        return get_summoner_info_from_puuid(puuid)
    else:
        response.raise_for_status()

def calculate_stats(summoner_name: str, tag_line: str, region: str, champion: str, match_count=10):
    try:
        summoner_info = get_summoner_info(summoner_name, tag_line, region)
    except Exception as e:
        print(f"Error getting summoner info: {e}")
        return None

    puuid = summoner_info["puuid"]
    
    puuid_summoner_info = get_summoner_info_from_puuid(puuid, region)
    profile_icon_id = puuid_summoner_info["profileIconId"]
    profile_summoner_level = puuid_summoner_info["summonerLevel"]
    print(profile_summoner_level)

    matches = get_recent_match_ids(puuid, region, count=match_count)

    wins = 0
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    total_cs = 0
    total_gold = 0
    total_damage = 0

    for idx, match_id in enumerate(matches):
        match_data = get_match_details(match_id, region)
        participants = match_data["info"]["participants"]

        # Find the participant data for our summoner
        participant = next((p for p in participants if p["puuid"] == puuid), None)
        if not participant:
            continue  # skip if not found (shouldn't happen)

        if idx == 0:
            champion_name = participant["championName"]  # set only for first match

        if participant["win"]:
            wins += 1

        total_kills += participant["kills"]
        total_deaths += participant["deaths"]
        total_assists += participant["assists"]
        total_cs += participant["totalMinionsKilled"] + participant.get("neutralMinionsKilled", 0)
        total_gold += participant["goldEarned"]
        total_damage += participant["totalDamageDealtToChampions"]

    games = len(matches)
    if games == 0:
        return None

    winrate = round((wins / games) * 100, 2)
    avg_kills = round(total_kills / games, 2)
    avg_deaths = round(total_deaths / games, 2)
    avg_assists = round(total_assists / games, 2)
    avg_cs = round(total_cs / games, 2)
    avg_gold = round(total_gold / games, 2)
    avg_damage = round(total_damage / games, 2)
    kda = f"{avg_kills} / {avg_deaths} / {avg_assists}"

    return {
        "name": summoner_name,
        "region": region.upper(),
        "winrate": winrate,
        "kda": kda,
        "avg_cs": avg_cs,
        "avg_gold": avg_gold,
        "avg_damage": avg_damage,
        "games": games,
        "champion": champion,
        "backup_champion": champion_name,
        "profile_icon_id": profile_icon_id
    }
