import discord
import os
from dotenv import load_dotenv
from riot_api import get_summoner_stats
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
    print("Received message:", message.content)
    if message.author == client.user:
        return

    if message.content.startswith('!lolstats'):
        parts = message.content.split()
        if len(parts) != 3:
            await message.channel.send("Usage: `!lolstats <summoner-name> <region>`")
            return

        summoner_name = parts[1]
        region = parts[2]
        await message.channel.send("Fetching summoner data...")

        stats = get_summoner_stats(summoner_name, region)
        image_path = generate_summary_image(stats)

        await message.channel.send(file=discord.File(image_path))

client.run(TOKEN)
