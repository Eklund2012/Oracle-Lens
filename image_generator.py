import io
from random import choice
from tkinter import font
from PIL import Image, ImageDraw, ImageFont
from exceptiongroup import catch
import requests
from io import BytesIO
from config.image_constants import *
from config.API_constants import BODY_JSON_RESPONSE

def get_random_skin(champ):
    # Fetch champion data to get available skins
    url = f"https://ddragon.leagueoflegends.com/cdn/15.16.1/data/en_US/champion/{champ}.json"
    response = requests.get(url)
    data = response.json()

    # Extract skin numbers
    skins = [skin["num"] for skin in data["data"][champ]["skins"]]

    # Pick a random skin
    skin_num = choice(skins)
    return skin_num

def get_champion_splash(stats):
    # Capitalize first letter (required by Riot's CDN)
    if stats["most_played_champion"]:
        champ = stats["most_played_champion"].capitalize()
    else:
        champ = stats["last_played_champion"].capitalize()
    print(f"Fetching splash art for champion: {champ}")

    skin_num = get_random_skin(champ)

    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_{skin_num}.jpg"

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
    draw = ImageDraw.Draw(icon, "RGBA")

    # Fonts
    name_font = ImageFont.truetype(title_font, size=ICON_FONT_SIZE)
    small_font = ImageFont.truetype(title_font, size=ICON_FONT_SIZE)

    # Text strings
    name_text = f"{stats['name']}"
    tagline_text = f"#{stats['tag_line']}"
    level_text = f"Level {stats['profile_summoner_level']}"

    # Padding values
    padding = ICON_FONT_Y_PADDING
    bottom_padding = 6  # extra space below the level

    # Helper to measure text
    def text_size(draw, text, font):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top

    name_w, name_h = text_size(draw, name_text, name_font)
    tagline_w, tagline_h = text_size(draw, tagline_text, small_font)
    level_w, level_h = text_size(draw, level_text, small_font)

    # Overlay height includes extra padding below level
    box_height = name_h + tagline_h + level_h + padding * 4 + bottom_padding
    y_start = icon.height - box_height + padding

    # Semi-transparent rectangle background
    overlay = Image.new("RGBA", (icon.width, box_height), (0, 0, 0, 150))
    icon.paste(overlay, (0, icon.height - box_height), overlay)

    # Draw shadow
    shadow_offset = 2
    for dx, dy in [(shadow_offset, shadow_offset)]:
        draw.text((padding + dx, y_start + dy), name_text, font=name_font, fill="black")
        draw.text((padding + dx, y_start + name_h + padding + dy), tagline_text, font=small_font, fill="black")
        draw.text((padding + dx, y_start + name_h + tagline_h + padding*2 + dy), level_text, font=small_font, fill="black")

    # Draw foreground text
    draw.text((padding, y_start), name_text, font=name_font, fill="white")
    draw.text((padding, y_start + name_h + padding), tagline_text, font=small_font, fill="white")
    draw.text((padding, y_start + name_h + tagline_h + padding*2), level_text, font=small_font, fill="white")

    return icon

def generate_summary_image(stats):
    bg = get_champion_splash(stats) or Image.new("RGB", FALLBACK_BG_SIZE, FALLBACK_BG_RGB) # Fallback background if splash not found

    icon = get_profile_icon(stats["profile_icon_id"])
    if icon:
        icon = generate_icon_image(icon, stats)
        bg.paste(icon, (0, 0))

    draw = ImageDraw.Draw(bg, "RGBA")
    font = ImageFont.truetype(title_font, size=40)

    # Stats to display
    stats_text = [
        f"Winrate: {stats['winrate']}%",
        f"KDA: {stats['kda']}",
        f"Average CS: {round(stats['avg_cs'], 1)}",
        f"Average Gold: {round(stats['avg_gold'], 0)}",
        f"Average Damage: {round(stats['avg_damage'], 0)}",
        f"Games Analyzed: {stats['games']}"
    ]

    # Padding & placement
    padding_x = 400
    padding_y = 40
    line_height = 50
    shadow_offset = 2

    # Semi-transparent overlay behind stats
    overlay_height = line_height * len(stats_text) + 40
    overlay_width = bg.width - padding_x - 40
    overlay = Image.new("RGBA", (overlay_width, overlay_height), (0, 0, 0, 150))
    bg.paste(overlay, (padding_x - 20, padding_y - 20), overlay)

    # Draw each line with shadow for readability
    for i, text in enumerate(stats_text):
        y = padding_y + i * line_height
        # Shadow
        draw.text((padding_x + shadow_offset, y + shadow_offset), text, font=font, fill="black")
        # Foreground
        draw.text((padding_x, y), text, font=font, fill="white")

    # Output as PNG in memory
    output = io.BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
