import discord
import os
from dotenv import load_dotenv
from riot_api import calculate_stats
from image_generator import generate_summary_image

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!lolstats'):
        print("Received !lolstats message:", message.content)
        parts = message.content.split()
        if len(parts) < 4:
            await message.channel.send("Usage: `!lolstats <summoner-name> <tag-line> <region> (optional)<champion>`")
            return

        summoner_name = parts[1]
        tag_line = parts[2]
        if tag_line.startswith("#"):
            tag_line = tag_line[1:]
        region = parts[3]
        champion = parts[4] if len(parts) > 4 else None
        await message.channel.send("Fetching summoner data...")

        stats = calculate_stats(summoner_name, tag_line, region, champion)
        if not stats:
            await message.channel.send("Failed to fetch stats, please check the summoner-name, tag-line and region.")
            return
        image_path = generate_summary_image(stats)

        await message.channel.send(file=discord.File(image_path))

client.run(TOKEN)
