import random
import requests
import os
import numpy as np
import math
import re
import unicodedata
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Define the API URL
API_URL = "https://api.artsy.net/api/"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# Define character brightness levels
CARACTER_BRIGHTNESS = {
    0: 'F', 1: 'T', 2: 'C', 3: 'L', 4: 'W', 5: 'E', 6: 'Y', 7: 'X', 8: 'U', 9: 'A',
    10: 'Z', 11: 'M', 12: 'Q', 13: 'O', 14: 'N', 15: 'D', 16: 'B', 17: '#', 18: '$',
    19: '&', 20: '@', 21: '%', 22: '^', 23: '(', 24: ')', 25: '[', 26: ']', 27: '{',
    28: '}', 29: '<', 30: '>', 31: '_', 32: '"', 33: "'", 34: '`', 35: ' ', 36: '.',
    37: ',', 38: ':', 39: ';', 40: '-', 41: '~', 42: '=', 43: '|', 44: '+', 45: '*',
    46: '?', 47: '!', 48: '/', 49: '\\', 50: 'i', 51: 'l', 52: 't', 53: 'v', 54: 'x',
    55: 'r', 56: 'c', 57: 'o', 58: 'f', 59: 'j', 60: 'u', 61: 'n', 62: 'x', 63: 'k',
    64: 'h', 65: 'a', 66: 'e', 67: 'y', 68: 'z', 69: 'm', 70: 'w', 71: 'g', 72: 'p',
    73: 'q', 74: 'd', 75: 'b', 76: 'R', 77: 'H', 78: 'S', 79: 'G', 80: 'F', 81: 'T',
    82: 'C', 83: 'L', 84: 'W', 85: 'E', 86: 'Y', 87: 'X', 88: 'U', 89: 'A', 90: 'Z',
    91: 'M', 92: 'Q', 93: 'O', 94: 'N', 95: 'D', 96: 'B', 97: '#', 98: '$', 99: '&',
    100: '@', 101: '%', 102: '^', 103: '(', 104: ')', 105: '[', 106: ']', 107: '{',
    108: '}', 109: '<', 110: '>', 111: '_', 112: '"', 113: "'", 114: '`', 115: ' ',
    116: '.', 117: ',', 118: ':', 119: ';', 120: '-', 121: '~', 122: '=', 123: '|',
    124: '+', 125: '*', 126: '?', 127: '!'
}


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
    return len(array) * [random.randint(12000, 18000) // 24]


def previous_artwork_gif():
    print("Creating GIF of previous artworks")
    artworks = []
    ascii_artworks = []
    for folder in os.listdir("previousArtworks"):
        if os.path.isdir("previousArtworks/" + folder):
            artwork = Image.open("previousArtworks/" + folder + "/artwork.jpg")
            ascii_artwork = Image.open("previousArtworks/" + folder + "/ascii_artwork.jpg")
            artworks.append(artwork)
            ascii_artworks.append(ascii_artwork)

    # all images should have the same size
    max_width = max(artwork.size[0] for artwork in artworks)
    max_height = max(artwork.size[1] for artwork in artworks)

    for i, artwork in enumerate(artworks):
        new_artwork = Image.new("RGB", (max_width, max_height), color="white")
        new_artwork.paste(artwork, ((max_width - artwork.size[0]) // 2, (max_height - artwork.size[1]) // 2))
        artworks[i] = new_artwork

    for i, ascii_artwork in enumerate(ascii_artworks):
        new_ascii_artwork = Image.new("RGB", (max_width, max_height), color="white")
        new_ascii_artwork.paste(ascii_artwork, ((max_width - ascii_artwork.size[0]) // 2, (max_height - ascii_artwork.size[1]) // 2))
        ascii_artworks[i] = new_ascii_artwork

    artworks[0].save("previousArtworks/previous_artworks.gif", save_all=True, append_images=artworks[1:], duration=duration(artworks), loop=0)
    ascii_artworks[0].save("previousArtworks/previous_ascii_artworks.gif", save_all=True, append_images=ascii_artworks[1:], duration=duration(ascii_artworks), loop=0)

    print("GIF created")


def generate_and_save_ascii_picture(image_path):
    print("Generating ASCII artwork")
    img = Image.open(image_path)
    width, height = img.size
    new_width = width * 4
    new_height = height * 4
    img = img.resize((new_width, new_height))
    img = img.convert("L")
    pixels = np.array(img)
    new_img = Image.new("RGB", (new_width, new_height), color="white")
    draw = ImageDraw.Draw(new_img)

    for y in range(0, new_height, 6):
        for x in range(0, new_width, 6):
            avg_brightness = np.mean(pixels[y:y + 6, x:x + 6])
            brightness = math.ceil(avg_brightness / 5)
            ascii_char = CARACTER_BRIGHTNESS[brightness]
            draw.text((x, y), ascii_char, fill="black", spacing=60)

    new_img = new_img.resize((math.floor(400 * new_width / new_height), 400))
    new_img.save("currentArtwork/ascii_artwork.jpg")
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

            new_artwork = Image.open("currentArtwork/artwork.jpg")
            width, height = new_artwork.size
            new_image_width = math.floor(400 * width / height)
            new_artwork = new_artwork.resize((new_image_width, 400))
            new_artwork.save("currentArtwork/artwork.jpg")
            print("Resized image")

            ascii_artwork = generate_and_save_ascii_picture("currentArtwork/artwork.jpg")

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
                ascii_artwork.save("previousArtworks/" + new_folder_name + "/ascii_artwork.jpg")
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


get_random_artwork(fetch_xapp_token(CLIENT_ID, CLIENT_SECRET, API_URL), API_URL)