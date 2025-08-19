# OracleLens

A Discord bot that fetches League of Legends match data using the Riot API and generates clean, visual stat summaries for any summoner. Perfect for players who want quick insights without digging through dashboards.

![OracleLens](assets/img/Oracle_Lens.png)

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
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
# Windows
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

### 5. Run the bot
Make sure you have your environment variables set up (like your Discord bot token and Riot API key), then start your bot:
```bash
python main.py
```

## Usage
Once the bot is running and added to your server, you can use the !lolstats command to fetch stats:

```bash
!lolstats <summoner-name> <tag-line> <region> (optional)<champion>
```
summoner-name → The player’s in-game name.

tag-line → The Riot tagline (with or without the #, e.g. NA1 or #NA1).

region → The server region (e.g., na, euw, kr).

champion (optional)

### Examples
```bash
!lolstats Faker KR1 kr
```
```bash
!lolstats Doublelift NA1 na Kai'Sa
```



## License
OracleLens isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
