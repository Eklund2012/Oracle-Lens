from PIL import Image, ImageDraw, ImageFont
import requests
from PIL import Image
from io import BytesIO

def get_champion_splash(champion_name):
    # Capitalize first letter (required by Riot's CDN)
    champ = champion_name.capitalize()
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg"

    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content)).resize((600, 300))
    else:
        print(f"Failed to get splash art for {champion_name}")
        return None


def generate_summary_image(stats):
    bg = get_champion_splash(stats["champion"]) or Image.new("RGB", (600, 300), (30, 30, 40))
    draw = ImageDraw.Draw(bg)
    font = ImageFont.load_default()

    draw.text((20, 20), f"Summoner: {stats['name']}", fill="white", font=font)
    draw.text((20, 40), f"Winrate: {stats['winrate']}%", fill="white", font=font)
    draw.text((20, 60), f"KDA: {stats['kda']}", fill="white", font=font)
    draw.text((20, 80), f"Average CS: {stats['avg_cs']}", fill="white", font=font)
    draw.text((20, 100), f"Average Gold: {stats['avg_gold']}", fill="white", font=font)
    draw.text((20, 120), f"Average Damage: {stats['avg_damage']}", fill="white", font=font)
    draw.text((20, 140), f"Games Analyzed: {stats['games']}", fill="white", font=font)

    image_path = "summary.png"
    bg.save(image_path)
    return image_path
