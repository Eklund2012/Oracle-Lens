# main.py

from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

REGION = "na1"
MATCH_REGION = "americas"

@app.get("/summoner/{summoner_name}")
def get_summoner_data(summoner_name: str):
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise HTTPException(status_code=404, detail="Summoner not found")
    return res.json()

@app.get("/match-history/{puuid}")
def get_match_history(puuid: str):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1"
    res = requests.get(url, headers=HEADERS)
    return res.json()

@app.get("/match/{match_id}")
def get_match_details(match_id: str):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json()
