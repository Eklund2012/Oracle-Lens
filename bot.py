import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from riot_api import RiotAPIClient
from image_generator import generate_summary_image
from config.bot_constants import *

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

if not RIOT_API_KEY or not TOKEN:
    raise ValueError("API/DISCORD TOKEN not found. Please set it in your .env file.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

riot_api_client = RiotAPIClient(RIOT_API_KEY)

async def send_message(message, content=None, file=None):
    if content and file:
        await message.channel.send(content, file=file)
    elif content:
        await message.channel.send(content)
    elif file:
        await message.channel.send(file=file)

def validate_match_count(count):
    if not isinstance(count, int) or not (1 <= count <= MAX_MATCH_COUNT):
        raise ValueError(f"Match count must be an integer between 1 and {MAX_MATCH_COUNT}.")
    
def validate_region(region):
    if region.lower() not in VALID_REGIONS:
        raise ValueError(f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}")

# Event when the bot is ready
@bot.event
async def on_ready():
    await riot_api_client.start()   # start persistent session
    print(f"Logged in as {bot.user}")

@bot.event
async def on_close():
    await riot_api_client.close()   # cleanup session when bot shuts down

@bot.hybrid_command(name="lolstats")
async def lolstats(ctx, summoner_name: str, tag_line: str, region: str, match_count: int = DEFAULT_MATCH_COUNT):
    """Fetches League of Legends stats for a summoner."""
    try:
        validate_match_count(match_count)
        validate_region(region)
    except ValueError as ve:
        await ctx.send(f"{ve}")
        return
    
    await ctx.send("Fetching summoner data...")

    if tag_line.startswith("#"):
        tag_line = tag_line[1:]

    try:
        async with ctx.typing():
            stats = await riot_api_client.calculate_stats(summoner_name, tag_line, region, match_count)
    except Exception as e:
        print(f"Error in calculate_stats: {e}")
        await ctx.send("An unexpected error occurred. Please try again later.")
        return

    if not stats:
        await ctx.send("Failed to fetch stats. Please check the summoner-name, tag-line, and region.")
        return

    file_obj = generate_summary_image(stats)  # returns BytesIO
    file_obj.seek(0)  # make sure pointer is at start
    await ctx.send(file=discord.File(file_obj, "summary.png"))

@bot.hybrid_command(name="help_lol")
async def help_lol(ctx):
    """Explains how to use the lolstats command."""
    await ctx.send(HELP_OUTPUT)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing arguments.\nUsage: `!lolstats <summoner-name> <tag-line> <region>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument type. Please check your inputs.")
    elif isinstance(error, commands.CommandInvokeError):
        original = getattr(error, "original", error)
        await ctx.send("⚠️ Something went wrong while fetching your stats. Please try again later.")
        print(f"CommandInvokeError: {original}")
    elif isinstance(error, commands.CommandNotFound):
        return  # ignore silently
    else:
        print(f"Unhandled error: {error}")
        await ctx.send("⚠️ An unexpected error occurred. The issue has been logged.")

bot.run(TOKEN)