import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from riot_api import RiotAPIClient
from image_generator import generate_summary_image
from config.bot_constants import MINIMUM_MESSAGE_LENGTH_LOLSTATS

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

if not RIOT_API_KEY or not TOKEN:
    raise ValueError("API/TOKEN not found. Please set it in your .env file.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

riot_client = RiotAPIClient(RIOT_API_KEY)

async def send_message(message, content=None, file=None):
    if content and file:
        await message.channel.send(content, file=file)
    elif content:
        await message.channel.send(content)
    elif file:
        await message.channel.send(file=file)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.hybrid_command(name="lolstats")
async def lolstats(ctx, summoner_name: str, tag_line: str, region: str, champion: str = None):
    """Fetches League of Legends stats for a summoner."""
    await ctx.send("Fetching summoner data...")

    try:
        stats = await riot_client.calculate_stats(summoner_name, tag_line, region, champion)
    except Exception as e:
        print(f"Error in calculate_stats: {e}")
        await ctx.send("An unexpected error occurred. Please try again later.")
        return

    if not stats:
        await ctx.send("Failed to fetch stats. Please check the summoner-name, tag-line, and region.")
        return

    image_path = generate_summary_image(stats)
    await ctx.send(file=discord.File(image_path))

@bot.hybrid_command(name="help_lol")
async def help_lol(ctx):
    """Explains how to use the lolstats command."""
    await ctx.send("Usage: `!lolstats <summoner-name> <tag-line> <region> (optional)<champion>`")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: `!lolstats <summoner-name> <tag-line> <region> (optional)<champion>`")
    elif isinstance(error, commands.CommandNotFound):
        return  # ignore unknown commands
    else:
        print(f"Unhandled error: {error}")
        await ctx.send("An unexpected error occurred.")

bot.run(TOKEN)

    
