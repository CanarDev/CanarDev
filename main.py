import random
import requests
import os
import numpy as np
import math
import sys
import re
import unicodedata
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

# Define the API URL
API_URL = "https://api.artsy.net/api/"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# ASCII rendering settings
ASCII_CHARSET = "".join(chr(c) for c in range(32, 127))
ASCII_FONT_SIZE = 14
# Fewer but bigger characters: they stay readable once the image is displayed in the README
ASCII_COLUMNS = 140  # along the longest side of the artwork
# Characters are drawn with a darkened tone of their pixel, keeps the shading of the artwork
ASCII_INK_TONE = 0.7
ASCII_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "C:/Windows/Fonts/consola.ttf",
]

# GIF settings: every frame is fitted into the same square canvas
GIF_SIZE = (540, 540)
# Limits the palette so the GIF of hundreds of frames stays under GitHub limits
GIF_COLORS = 64


def fetch_xapp_token(client_id, client_secret, api_url):
    try:
        response = requests.post(api_url + 'tokens/xapp_token',
                                 json={"client_id": client_id, "client_secret": client_secret})
        if response.status_code == 201:
            return response.json().get("token")
        else:
            print("Failed to fetch xapp token. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def slugify(text):

    # Normalize the text to NFKD (Normalization Form KD)
    text = unicodedata.normalize('NFKD', text)

    # Encode the text to ASCII bytes and decode back to a string, ignoring non-ASCII characters
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase
    text = text.lower()

    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Remove leading and trailing hyphens
    text = text.strip('-')

    return text

def duration(array):
    return len(array) * 2250 // 24


def fit_on_canvas(image, size):
    image = image.convert("RGB")
    ratio = min(size[0] / image.size[0], size[1] / image.size[1])
    new_size = (max(1, round(image.size[0] * ratio)), max(1, round(image.size[1] * ratio)))
    image = image.resize(new_size, Image.LANCZOS)
    canvas = Image.new("RGB", size, color="white")
    canvas.paste(image, ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2))
    return canvas


def previous_artwork_gif():
    print("Creating GIF of previous artworks")
    artworks = []
    ascii_artworks = []
    for folder in sorted(os.listdir("previousArtworks")):
        if os.path.isdir("previousArtworks/" + folder):
            artwork = fit_on_canvas(Image.open("previousArtworks/" + folder + "/artwork.jpg"), GIF_SIZE)
            artworks.append(artwork.quantize(GIF_COLORS, dither=Image.Dither.NONE))
            ascii_artwork = fit_on_canvas(Image.open("previousArtworks/" + folder + "/ascii_artwork.jpg"), GIF_SIZE)
            # Black text on white only needs a few grey levels, keeps the GIF light
            ascii_artworks.append(ascii_artwork.convert("L").quantize(16, dither=Image.Dither.NONE))

    artworks[0].save("previousArtworks/previous_artworks.gif", save_all=True, append_images=artworks[1:], duration=duration(artworks), loop=0, optimize=True)
    ascii_artworks[0].save("previousArtworks/previous_ascii_artworks.gif", save_all=True, append_images=ascii_artworks[1:], duration=duration(ascii_artworks), loop=0, optimize=True)

    print("GIF created")


def load_ascii_font():
    for path in ASCII_FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, ASCII_FONT_SIZE)
    return ImageFont.load_default(ASCII_FONT_SIZE)


def build_char_ramp(font, cell_width, cell_height):
    # Measure how much ink each character really puts in its cell, so the ramp matches the font
    coverages = []
    for char in ASCII_CHARSET:
        cell = Image.new("L", (cell_width, cell_height), color=0)
        ImageDraw.Draw(cell).text((0, 0), char, fill=255, font=font)
        coverages.append((np.asarray(cell).mean(), char))
    coverages.sort()

    lowest, highest = coverages[0][0], coverages[-1][0]
    densities = np.array([(c - lowest) / (highest - lowest) for c, _ in coverages])
    chars = [char for _, char in coverages]

    # Lookup table: pixel brightness (0-255) -> char whose ink density best matches its darkness
    darkness = 1 - np.arange(256) / 255
    indexes = np.abs(densities[None, :] - darkness[:, None]).argmin(axis=1)
    return np.array(chars)[indexes]


def generate_ascii_picture(image_path):
    img = Image.open(image_path).convert("L")
    # Spread the tones over the whole character ramp, otherwise mid-tones all end up as the same dense glyph
    img = Image.blend(ImageOps.autocontrast(img, cutoff=1), ImageOps.equalize(img), 0.3)

    font = load_ascii_font()
    ascent, descent = font.getmetrics()
    cell_width = max(1, round(font.getlength("M")))
    cell_height = ascent + descent
    ramp = build_char_ramp(font, cell_width, cell_height)

    # Sample one pixel per character, compensating for the non-square character cells
    width, height = img.size
    columns = max(1, round(ASCII_COLUMNS * min(1, width / height)))
    rows = max(1, round(columns * (height / width) * (cell_width / cell_height)))
    # Sharpen after downscaling so contours survive the low character resolution
    small = img.resize((columns, rows), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))
    pixels = np.asarray(small)

    text_img = Image.new("L", (columns * cell_width, rows * cell_height), color=255)
    draw = ImageDraw.Draw(text_img)
    for y in range(rows):
        for x in range(columns):
            brightness = pixels[y, x]
            char = ramp[brightness]
            if char != " ":
                draw.text((x * cell_width, y * cell_height), char, fill=int(brightness * ASCII_INK_TONE), font=font)

    # Keep exactly the same aspect ratio as the original artwork
    output_size = (text_img.size[0], round(text_img.size[0] * height / width))
    return text_img.resize(output_size, Image.LANCZOS).convert("RGB")


def generate_and_save_ascii_picture(image_path):
    print("Generating ASCII artwork")
    new_img = generate_ascii_picture(image_path)
    new_img.save("currentArtwork/ascii_artwork.jpg", quality=95, subsampling=0)
    print("ASCII artwork generated")

    return new_img


def duplicate_readme(template_path, readme_path, title, date, rights, medium, category, art_link):

    if os.path.exists(readme_path):
        os.remove(readme_path)

    with open(template_path, "r") as f:
        template = f.read()

        template = template.replace("{{ name }}", title)
        template = template.replace("{{ date }}", date)
        template = template.replace("{{ picture_rights }}", rights)
        template = template.replace("{{ medium }}", medium)
        template = template.replace("{{ category }}", category)
        template = template.replace("{{ art_link }}", art_link)

        with open(readme_path, "w") as f:
            f.write(template)


def get_random_artwork(xapp_token, api_url):
    try:
        url = api_url + 'artworks?offset=' + str(random.randint(0, 10000)) + '&size=1&page=1'
        response = requests.get(url, headers={"X-Api-Key": xapp_token})
        if response.status_code == 200:
            print("Fetched artwork")
            artwork = response.json()
            title = artwork["_embedded"]["artworks"][0]["title"]
            date = artwork["_embedded"]["artworks"][0]["date"] or "Unknown"
            rights = artwork["_embedded"]["artworks"][0]["image_rights"]
            medium = artwork["_embedded"]["artworks"][0]["medium"] or "Unknown"
            category = artwork["_embedded"]["artworks"][0]["category"] or "Unknown"
            art_link = artwork["_embedded"]["artworks"][0]["_links"]["permalink"]["href"]
            artwork_id = artwork["_embedded"]["artworks"][0]["id"]

            image_url = artwork["_embedded"]["artworks"][0]["_links"]["image"]["href"]
            image_url = image_url.replace("{image_version}", "large")

            if os.path.exists("currentArtwork/artwork.jpg"):
                os.remove("currentArtwork/artwork.jpg")
                print("Removed current artwork")
            image = requests.get(image_url)

            with open("currentArtwork/artwork.jpg", "wb") as f:
                f.write(image.content)
                print("setting up image")

            # Build the ASCII version from the full resolution image for a sharper result
            ascii_artwork = generate_and_save_ascii_picture("currentArtwork/artwork.jpg")

            new_artwork = Image.open("currentArtwork/artwork.jpg").convert("RGB")
            width, height = new_artwork.size
            new_image_width = math.floor(400 * width / height)
            new_artwork = new_artwork.resize((new_image_width, 400), Image.LANCZOS)
            new_artwork.save("currentArtwork/artwork.jpg")
            print("Resized image")

            current_date = datetime.now().strftime("%Y-%m-%d")
            folder_artwork_title = slugify(title)
            new_folder_name = current_date + "-" + folder_artwork_title

            if not os.path.exists("previousArtworks/" + new_folder_name):
                os.makedirs("previousArtworks/" + new_folder_name)
                # Create md file with artwork details

                if os.path.exists("previousArtworks/" + new_folder_name + "/README.md"):
                    os.remove("previousArtworks/" + new_folder_name + "/README.md")

                with open("previousArtworks/template-current.md", "r") as f:
                    template = f.read()

                    template = template.replace("{{ name }}", title)
                    template = template.replace("{{ date }}", date)
                    template = template.replace("{{ picture_rights }}", rights)
                    template = template.replace("{{ medium }}", medium)
                    template = template.replace("{{ category }}", category)
                    template = template.replace("{{ art_link }}", art_link)

                    with open("previousArtworks/" + new_folder_name + "/README.md", "w") as f:
                        f.write(template)

                print("Created folder for previous artwork")

                new_artwork.save("previousArtworks/" + new_folder_name + "/artwork.jpg")
                ascii_artwork.save("previousArtworks/" + new_folder_name + "/ascii_artwork.jpg", quality=95, subsampling=0)
                print("Saved previous artwork")

                previous_artwork_gif()

            if os.path.exists("README.md"):
                os.remove("README.md")

            with open("template.md", "r") as f:
                template = f.read()

                template = template.replace("{{ name }}", title)
                template = template.replace("{{ date }}", date)
                template = template.replace("{{ picture_rights }}", rights)
                template = template.replace("{{ medium }}", medium)
                template = template.replace("{{ category }}", category)
                template = template.replace("{{ art_link }}", art_link)

                with open("README.md", "w") as f:
                    f.write(template)


        else:
            print("Failed to fetch artwork. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def regenerate_previous_ascii_artworks():
    print("Regenerating ASCII version of previous artworks")
    for folder in sorted(os.listdir("previousArtworks")):
        folder_path = "previousArtworks/" + folder
        if os.path.isdir(folder_path):
            generate_ascii_picture(folder_path + "/artwork.jpg").save(folder_path + "/ascii_artwork.jpg", quality=95, subsampling=0)
    generate_and_save_ascii_picture("currentArtwork/artwork.jpg")
    previous_artwork_gif()


if "--regenerate" in sys.argv:
    regenerate_previous_ascii_artworks()
else:
    get_random_artwork(fetch_xapp_token(CLIENT_ID, CLIENT_SECRET, API_URL), API_URL)
