# OracleLens

A Discord bot that fetches League of Legends match data using the Riot API and generates
clean, visual stat summaries for any summoner. Perfect for players who want quick insights
without digging through dashboards.

Built with Python to showcase backend/API integration, image generation, and bot development.

## Setup
Follow these steps to get OracleLens running locally:

### 1. Clone the repository
```bash
git clone https://github.com/Eklund2012/Oracle-Lens.git
cd OracleLens
```

### 2. Create a virtual environment
It’s recommended to use a virtual environment to keep dependencies isolated:
#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
#### Windows
```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install dependencies
Make sure requirements.txt is up to date, then install all required packages:
```bash
pip install -r requirements.txt
```

### 4. Verify installation
You can check that all packages are installed correctly:
```bash
pip list
```

### 5. Configure environment variables
Create a `.env` file in the project root with the following variables:
```env
DISCORD_TOKEN=your_discord_bot_token_here
RIOT_API_KEY=your_riot_api_key_here
```

DISCORD_TOKEN → Your Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

RIOT_API_KEY → Your Riot API key from the [Riot Developer Portal](https://developer.riotgames.com/)


### 6. Run the bot
Make sure you have your environment variables set up and dependecies installed then start your bot:
```bash
python bot.py
```

## Usage
Once the bot is running and added to your server, you can use the !lolstats command to fetch
stats:

```text
!lolstats <summoner-name> <tag-line> <region> (optional)<match-count>
```
summoner-name → The player’s in-game name.

tag-line → The Riot tagline (with or without the #, e.g. EUW or #EUW).

region → The server region (e.g., na, euw, kr, NA, EUW, KR).

match-count → amount of games to be analyzed (more games = longer wait time) 

```text
!help_lol
```
Typing !help_lol will give explantion of how to use the bot commands

### Examples
```text
!lolstats TheBausffs #COOL EUW
```
```text
!lolstats Clayray EUW euw 30
```

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

OracleLens isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot
Games or anyone officially involved in producing or managing Riot Games properties. Riot
Games, and all associated properties are trademarks or registered trademarks of Riot Games,
Inc.

## Contact
david.eklund9@gmail.com