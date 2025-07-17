from PIL import Image, ImageDraw, ImageFont

def generate_summary_image(stats):
    img = Image.new("RGB", (600, 300), color=(30, 30, 40))
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()
    draw.text((20, 20), f"Summoner: {stats['name']}", fill="white", font=font)
    draw.text((20, 60), f"Winrate: {stats['winrate']}%", fill="white", font=font)
    draw.text((20, 100), f"KDA: {stats['kda']}", fill="white", font=font)

    image_path = "summary.png"
    img.save(image_path)
    return image_path
