# ----------------- Bot Constants -----------------

# Maximum number of recent matches that can be fetched for a summoner.
# Prevents overloading the Riot API and keeps response times reasonable.
MAX_MATCH_COUNT = 100

# Default number of matches to fetch if the user does not specify a match count.
DEFAULT_MATCH_COUNT = 25

# Cooldown in seconds for the !lolstats command per user.
# Prevents spam and excessive API calls.
LOLSTATS_COOLDOWN = 10

# Help message displayed by the !help_lol command.
# Explains available commands and their usage.
HELP_OUTPUT = """
Available commands:
- Fetch League of Legends stats for a player: 
  `!lolstats <summoner_name> <tag_line> <region> (optional)<match_amount>`
- Show this help message: 
  `!help_lol`
"""

# List of valid regions for Riot API requests.
# Used to validate user input and ensure API calls are made to the correct server.
VALID_REGIONS = ["na", "euw", "eune", "kr", "br", "jp", "oc", "ru", "tr"]
