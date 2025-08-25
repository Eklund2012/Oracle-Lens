import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from riot_api import RiotAPIClient
from image_generator import generate_summary_image
from config.bot_constants import HELP_OUTPUT

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
    if not isinstance(count, int) or not (1 <= count <= 100):
        raise ValueError("Match count must be an integer between 1 and 100.")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.hybrid_command(name="lolstats")
async def lolstats(ctx, summoner_name: str, tag_line: str, region: str, match_count: int = 25):
    """Fetches League of Legends stats for a summoner."""
    try:
        validate_match_count(match_count)
    except ValueError as ve:
        await ctx.send(f"{ve}")
        return
    
    await ctx.send("Fetching summoner data...")

    if tag_line.startswith("#"):
        tag_line = tag_line[1:]

    try:
        stats = await riot_api_client.calculate_stats(summoner_name, tag_line, region, match_count)
    except Exception as e:
        print(f"Error in calculate_stats: {e}")
        await ctx.send("An unexpected error occurred. Please try again later.")
        return

    if not stats:
        await ctx.send("Failed to fetch stats. Please check the summoner-name, tag-line, and region.")
        return

    #image_path = generate_summary_image(stats)
    await ctx.send(file=discord.File(generate_summary_image(stats), "summary.png"))

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
        # This wraps errors inside commands (like API failures)
        original = getattr(error, "original", error)
        await ctx.send(f"⚠️ An error occurred (flame Madao)")
        print(f"CommandInvokeError: {original}")
    elif isinstance(error, commands.CommandNotFound):
        return  # ignore silently
    else:
        print(f"Unhandled error: {error}")
        await ctx.send("⚠️ An unexpected error occurred. The issue has been logged.")

bot.run(TOKEN)