import io
import logging
import time
from random import choice
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from config.image_constants import *
from config.API_constants import BODY_JSON_RESPONSE

_version_cache = {"value": None, "timestamp": 0}
CACHE_TTL = ONE_HOUR  # refresh every hour

def get_latest_version():
    now = time.time()
    if _version_cache["value"] and now - _version_cache["timestamp"] < CACHE_TTL:
        return _version_cache["value"]
    logging.debug("Fetching latest version from API")
    print("Fetching latest version from API")

    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    response.raise_for_status()
    versions = response.json()
    latest = versions[0]

    _version_cache.update({"value": latest, "timestamp": now})
    return latest

def get_random_skin(champ):
    url = f"https://ddragon.leagueoflegends.com/cdn/{get_latest_version()}/data/en_US/champion/{champ}.json"
    response = requests.get(url)
    if response.status_code != BODY_JSON_RESPONSE: # 200
        raise ValueError(f"Failed to fetch skins for {champ}: "
                         f"HTTP {response.status_code} - {response.text[:BODY_JSON_RESPONSE]}")
    try:
        data = response.json()
    except Exception as e:
        raise ValueError(f"Invalid JSON for {champ}: {e} (body={response.text[:BODY_JSON_RESPONSE]})")

    skins = [skin["num"] for skin in data["data"][champ]["skins"]]
    return choice(skins)

def get_champion_splash(stats):
    champ = stats.get("most_played_champion") or stats.get("last_played_champion")
    if not champ:
        print("No champion provided in stats")
        return None
    
    champ = champ.strip()  # remove trailing spaces just in case
    print(f"Fetching splash art for champion: {champ}")

    try:
        skin_num = get_random_skin(champ)
    except Exception as e:
        print(f"Error getting skins for {champ}: {e}")
        return None

    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_{skin_num}.jpg"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error fetching champion splash for {champ}: {e}")
        return None

def get_profile_icon(icon_id):
    url = f"https://ddragon.leagueoflegends.com/cdn/{get_latest_version()}/img/profileicon/{icon_id}.png"
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
    overlay = Image.new("RGBA", (icon.width, box_height), STATS_RGBA)
    icon.paste(overlay, (0, icon.height - box_height), overlay)

    # Draw shadow
    shadow_offset = STATS_SHADOW_OFFSET
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
    bg = get_champion_splash(stats) or Image.new("RGB", CHAMPION_SPLASH_SIZE, FALLBACK_BG_RGB) # Fallback background if splash not found

    icon = get_profile_icon(stats["profile_icon_id"]) or Image.new("RGB", PROFILE_ICON_SIZE, FALLBACK_ICON_RGB)
    if icon:
        icon = generate_icon_image(icon, stats)
        bg.paste(icon, (0, 0))

    draw = ImageDraw.Draw(bg, "RGBA")
    font = ImageFont.truetype(title_font, size=STATS_FONT_SIZE)

    # Stats to display
    single_game = stats['games'] == 1
    stats_text = [
        f"Winrate: {stats['winrate']}%",
        f"KDA: {stats['kda']}",
        f"{'CS' if single_game else 'Average CS'}: {round(stats['avg_cs'], 1)}",
        f"CS per Minute: {stats['cs_per_min']}",
        f"{'Gold' if single_game else 'Average Gold'}: {round(stats['avg_gold'], 0)}",
        f"{'Damage' if single_game else 'Average Damage'}: {round(stats['avg_damage'], 0)}",
        f"Games Analyzed: {stats['games']}"
    ]


    # Padding & placement
    padding_x = STATS_PADDING_X
    padding_y = STATS_PADDING_Y
    line_height = STATS_LINE_HEIGHT
    shadow_offset = STATS_SHADOW_OFFSET

    # Semi-transparent overlay behind stats
    overlay_height = line_height * len(stats_text) + STATS_FONT_SIZE
    overlay_width = bg.width - padding_x - STATS_FONT_SIZE
    overlay = Image.new("RGBA", (overlay_width, overlay_height), STATS_RGBA)
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
