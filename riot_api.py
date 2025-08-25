from collections import Counter
import aiohttp
import asyncio
from config.API_constants import *

class RiotAPIError(Exception):
    pass

class RiotAPIClient:
    def __init__(self, api_key: str, rate_limit_timeout: int = DISCORD_RATE_LIMIT_TIMEOUT):
        self.api_key = api_key
        self.rate_limit_timeout = rate_limit_timeout

    def get_platform_and_regional(self, region: str):
        """Return platform and regional routing values for the given region."""
        platform = REGION_TO_PLATFORM.get(region.upper())
        regional = REGION_TO_REGIONAL.get(region.upper())
        if not platform or not regional:
            raise ValueError(
                f"Unsupported region '{region}'. Supported: {list(REGION_TO_PLATFORM.keys())}"
            )
        return platform, regional

    async def send_request(self, url: str, params: dict = None):
        headers = {"X-Riot-Token": self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == BODY_JSON_RESPONSE:  # 200
                    return await response.json()
                elif response.status == RATE_LIMIT_EXCEEDED:  # 429
                    retry_after = int(response.headers.get("Retry-After", self.rate_limit_timeout))
                    print(f"Rate limit exceeded, waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    return await self.send_request(url, params)
                else:
                    error_text = await response.text()
                    raise RiotAPIError(
                        f"Riot API error {response.status} on {url} with params {params}: {error_text}"
                    )

    async def get_summoner_info(self, summoner_name: str, tag_line: str, region: str):
        _, regional = self.get_platform_and_regional(region)
        url = f"https://{regional}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}"
        return await self.send_request(url)

    async def get_summoner_info_from_puuid(self, puuid: str, region: str):
        platform, _ = self.get_platform_and_regional(region)
        url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self.send_request(url)

    async def get_recent_match_ids(self, puuid: str, region: str, count: int = FETCHED_PARTICIPANT_MATCHES):
        _, regional = self.get_platform_and_regional(region)
        url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        return await self.send_request(url, params)

    async def get_match_details(self, match_id: str, region: str):
        _, regional = self.get_platform_and_regional(region)
        url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return await self.send_request(url)

    async def fetch_participant_matches(self, puuid: str, region: str, match_count: int = FETCHED_PARTICIPANT_MATCHES, max_concurrent: int = SEMAPHORE_LIMIT):
        """
        Return participant match data for the latest `match_count` matches.
        Fetches match details concurrently, throttled by `max_concurrent` to avoid hitting rate limits.
        """
        matches = await self.get_recent_match_ids(puuid, region, count=match_count)
        participant_matches = []

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_one(match_id):
            async with semaphore:
                try:
                    match_data = await self.get_match_details(match_id, region)
                    participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
                    return participant
                except Exception as e:
                    print(f"Failed to fetch match {match_id}: {e}")
                    return None

        results = await asyncio.gather(*(fetch_one(mid) for mid in matches))

        # Filter out None results
        participant_matches = [p for p in results if p is not None]

        return participant_matches

    @staticmethod
    def aggregate_match_stats(participant_matches: list[dict]) -> dict[str, float] | None:
        """Aggregate stats from a list of participant dicts."""
        if not participant_matches:
            return None

        total = {
            "wins": 0,
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "cs": 0,
            "gold": 0,
            "damage": 0,
        }

        for p in participant_matches:
            if p["win"]:
                total["wins"] += 1
            total["kills"] += p["kills"]
            total["deaths"] += p["deaths"]
            total["assists"] += p["assists"]
            total["cs"] += p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0)
            total["gold"] += p["goldEarned"]
            total["damage"] += p["totalDamageDealtToChampions"]

        games = len(participant_matches)
        return {
            "winrate": round((total["wins"] / games) * 100, 2),
            "avg_kills": round(total["kills"] / games, 2),
            "avg_deaths": round(total["deaths"] / games, 2),
            "avg_assists": round(total["assists"] / games, 2),
            "avg_cs": round(total["cs"] / games, 2),
            "avg_gold": round(total["gold"] / games, 2),
            "avg_damage": round(total["damage"] / games, 2),
            "games": games,
        }

    async def calculate_stats(self, summoner_name: str, tag_line: str, region: str, match_count: int = FETCHED_PARTICIPANT_MATCHES):
        """Fetch summoner stats and return aggregated performance metrics."""
        try:
            summoner_info = await self.get_summoner_info(summoner_name, tag_line, region)
        except RiotAPIError as e:
            print(f"Riot API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        try:
            puuid = summoner_info["puuid"]
            puuid_info = await self.get_summoner_info_from_puuid(puuid, region)
            profile_icon_id = puuid_info["profileIconId"]
            profile_summoner_level = puuid_info["summonerLevel"]
        except Exception as e:
            print(f"Error fetching summoner info: {e}")
            return None

        participant_matches = await self.fetch_participant_matches(puuid, region, match_count)
        if not participant_matches:
            return None

        stats = self.aggregate_match_stats(participant_matches)
        last_played_champion = participant_matches[0]["championName"] if participant_matches else None
        # Most played champion
        champion_counts = Counter(p["championName"] for p in participant_matches)
        most_played_champion, most_played_count = champion_counts.most_common(1)[0]
        if most_played_count == 1 and len(champion_counts) > 1:
            most_played_champion = None

        return {
            "name": summoner_name,
            "region": region.upper(),
            "tag_line": tag_line,
            "winrate": stats["winrate"],
            "kda": f"{stats['avg_kills']} / {stats['avg_deaths']} / {stats['avg_assists']}",
            "avg_cs": stats["avg_cs"],
            "avg_gold": stats["avg_gold"],
            "avg_damage": stats["avg_damage"],
            "games": stats["games"],
            "last_played_champion": last_played_champion,
            "most_played_champion": most_played_champion,
            "most_played_count": most_played_count,
            "profile_icon_id": profile_icon_id,
            "profile_summoner_level": profile_summoner_level,
        }
