import discord
import os
import logging
from discord.ext import commands
from dotenv import load_dotenv
from riot_api import RiotAPIClient
from image_generator import generate_summary_image
from config.bot_constants import *

# ----------------- Logging -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ----------------- Load Environment -----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

if not RIOT_API_KEY or not TOKEN:
    logger.critical("API/DISCORD TOKEN not found. Please set it in your .env file.")
    raise ValueError("Missing API/DISCORD token.")

# ----------------- Intents -----------------
intents = discord.Intents.default()
intents.message_content = True

# ----------------- Riot API -----------------
riot_api_client = RiotAPIClient(RIOT_API_KEY)

# ----------------- Custom Bot Class -----------------
class MyBot(commands.Bot):
    async def close(self):
        logger.info("Shutting down Riot API session...")
        await riot_api_client.close()
        await super().close()

bot = MyBot(command_prefix="!", intents=intents)

# ----------------- Helper Functions -----------------
def validate_match_count(count):
    if not isinstance(count, int) or not (1 <= count <= MAX_MATCH_COUNT):
        raise ValueError(f"Match count must be an integer between 1 and {MAX_MATCH_COUNT}.")

def validate_region(region):
    if region.lower() not in VALID_REGIONS:
        raise ValueError(f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}")

# ----------------- Events -----------------
@bot.event
async def on_ready():
    await riot_api_client.start()  # Start Riot API session
    await bot.tree.sync()          # Sync hybrid/slash commands
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Timeout: try again in {error.retry_after:.0f} seconds.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing arguments.\nUsage: `!lolstats <summoner-name> <tag-line> <region>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument type. Please check your inputs.")
    elif isinstance(error, commands.CommandInvokeError):
        original = getattr(error, "original", error)
        logger.exception(f"CommandInvokeError: {original}")
        await ctx.send("⚠️ Something went wrong while fetching your stats. Please try again later.")
    elif isinstance(error, commands.CommandNotFound):
        return  # ignore silently
    else:
        logger.exception(f"Unhandled error: {error}")
        await ctx.send("⚠️ An unexpected error occurred. The issue has been logged.")

# ----------------- Commands -----------------
@bot.hybrid_command(name="lolstats")
@commands.cooldown(1, LOLSTATS_COOLDOWN, commands.BucketType.user) # cooldown per-user 10s
async def lolstats(ctx, summoner_name: str, tag_line: str, region: str, match_count: int = DEFAULT_MATCH_COUNT):
    logger.info(f"{ctx.author} invoked lolstats: {summoner_name} #{tag_line} in {region}")
    """Fetches League of Legends stats for a summoner."""
    try:
        validate_match_count(match_count)
        validate_region(region)
    except ValueError as ve:
        await ctx.send(f"{ve}")
        return

    await ctx.send("🔍 Fetching summoner data...")

    if tag_line.startswith("#"):
        tag_line = tag_line[1:].strip()

    try:
        async with ctx.typing():
            stats = await riot_api_client.calculate_stats(summoner_name, tag_line, region, match_count)
    except Exception as e:
        logger.exception(f"Error fetching stats: {e}")
        await ctx.send("An unexpected error occurred. Please try again later.")
        return

    if not stats:
        await ctx.send("Failed to fetch stats. Please check the summoner-name, tag-line, and region.")
        return

    file_obj = generate_summary_image(stats)
    file_obj.seek(0)
    await ctx.send(file=discord.File(file_obj, "summary.png"))

@bot.hybrid_command(name="help_lol")
async def help_lol(ctx):
    """Explains how to use the lolstats command."""
    await ctx.send(HELP_OUTPUT)

# ----------------- Run Bot -----------------
bot.run(TOKEN)