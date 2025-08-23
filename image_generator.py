import io
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from config.image_constants import title_font, body_font

def get_champion_splash(stats):
    # Capitalize first letter (required by Riot's CDN)
    if stats["last_played_champion"]:
        champ = stats["last_played_champion"].capitalize()
    print(f"Fetching splash art for champion: {champ}")
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg"

    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content)).resize((600, 300))
    else:
        print(f"Failed to get splash art for {champ}")
        return None

def get_profile_icon(icon_id):
    url = f"https://ddragon.leagueoflegends.com/cdn/15.14.1/img/profileicon/{icon_id}.png"
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print(f"Failed to get profile icon for ID {icon_id}")
        return None

def generate_summary_image(stats):
    bg = get_champion_splash(stats) or Image.new("RGB", (600, 300), (30, 30, 40))
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 100))  # Black transparent layer
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)
    lol_logo = Image.open("assets/img/lol.png").resize((65, 50))
    bg.paste(lol_logo, (535, 250), lol_logo.convert("RGBA"))
    icon = get_profile_icon(stats["profile_icon_id"])
    if icon:
        icon = icon.resize((80, 80))
        bg.paste(icon, (510, 10))
        
    draw = ImageDraw.Draw(bg)

    font = ImageFont.truetype(title_font, size=25)

    # Draw level badge
    badge_size = 30
    badge = Image.new("RGBA", (badge_size, badge_size), (0,0,0,180))
    bg.paste(badge, (510+50, 10+50), badge)  # bottom-right corner av ikonen
    draw.text((510+55, 10+55), f"{stats['profile_summoner_level']}", fill="white", font=font)

    draw.text((20, 20), f"{stats['name']} #{stats['tag_line']}", fill="white", font=font)
    draw.text((20, 40), f"Winrate: {stats['winrate']}%", fill="white", font=font)
    draw.text((20, 60), f"KDA: {stats['kda']}", fill="white", font=font)
    draw.text((20, 80), f"Average CS: {stats['avg_cs']}", fill="white", font=font)
    draw.text((20, 100), f"Average Gold: {stats['avg_gold']}", fill="white", font=font)
    draw.text((20, 120), f"Average Damage: {stats['avg_damage']}", fill="white", font=font)
    draw.text((20, 140), f"Games Analyzed: {stats['games']}", fill="white", font=font)

    output = io.BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
