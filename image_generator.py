import io
from tkinter import font
from PIL import Image, ImageDraw, ImageFont
from exceptiongroup import catch
import requests
from io import BytesIO
from config.image_constants import *
from config.API_constants import BODY_JSON_RESPONSE

def get_champion_splash(stats):
    # Capitalize first letter (required by Riot's CDN)
    if stats["most_played_champion"]:
        champ = stats["most_played_champion"].capitalize()
    else:
        champ = stats["last_played_champion"].capitalize()
    print(f"Fetching splash art for champion: {champ}")
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg"

    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Error fetching champion splash: {e}")
        return None
    if response.status_code == BODY_JSON_RESPONSE: # 200 OK
        #return Image.open(BytesIO(response.content)).resize((600, 300))
        return Image.open(BytesIO(response.content)) # returns image of size (1215, 717)
    else:
        print(f"Failed to get splash art for {champ}")
        return None

def get_profile_icon(icon_id):
    url = f"https://ddragon.leagueoflegends.com/cdn/15.14.1/img/profileicon/{icon_id}.png"
    response = requests.get(url)
    if response.status_code == BODY_JSON_RESPONSE: # 200 OK
        return Image.open(BytesIO(response.content)) # returns image of size (300, 300)
    else:
        print(f"Failed to get profile icon for ID {icon_id}")
        return None
    
def generate_icon_image(icon, stats):
    draw = ImageDraw.Draw(icon)
    icon_title_font = ImageFont.truetype(title_font, size=ICON_FONT_SIZE)
    draw.text((0, 0), f"{stats['name']} #{stats['tag_line']}", fill="white", font=icon_title_font)
    draw.text((0, ICON_FONT_Y_PADDING), f"{stats['profile_summoner_level']}", fill="white", font=icon_title_font)
    return icon

def generate_summary_image(stats):
    bg = get_champion_splash(stats) or Image.new("RGB", FALLBACK_BG_SIZE, FALLBACK_BG_RGB) # Fallback background if splash not found

    icon = get_profile_icon(stats["profile_icon_id"])
    if icon:
        icon = generate_icon_image(icon, stats)
        bg.paste(icon, (0, 0))
        
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(title_font, size=25)

    
    '''
    
    draw.text((20, 40), f"Winrate: {stats['winrate']}%", fill="white", font=font)
    draw.text((20, 60), f"KDA: {stats['kda']}", fill="white", font=font)
    draw.text((20, 80), f"Average CS: {stats['avg_cs']}", fill="white", font=font)
    draw.text((20, 100), f"Average Gold: {stats['avg_gold']}", fill="white", font=font)
    draw.text((20, 120), f"Average Damage: {stats['avg_damage']}", fill="white", font=font)
    draw.text((20, 140), f"Games Analyzed: {stats['games']}", fill="white", font=font)
    '''
    output = io.BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
