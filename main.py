import sys, random, argparse, requests, os
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont

# Define the API URL
api_url = "https://api.artsy.net/api/"
client_id = "b813895670477893902f"
client_secret = "6c4774c8a0a0186b2aab4527095b917e"


def fetch_xapp_token(client_id, client_secret, api_url):
    try:
        response = requests.post(api_url + 'tokens/xapp_token',
                                 json={"client_id": client_id, "client_secret": client_secret})
        if response.status_code == 201:
            xapp_token = response.json().get("token")
            return xapp_token
        else:
            print("Failed to fetch xapp token. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def generate_ascii_picture(image_path):
    # Define caracter brightness levels
    caracter_brightness = {
        0: 'F',
        1: 'T',
        2: 'C',
        3: 'L',
        4: 'W',
        5: 'E',
        6: 'Y',
        7: 'X',
        8: 'U',
        9: 'A',
        10: 'Z',
        11: 'M',
        12: 'Q',
        13: 'O',
        14: 'N',
        15: 'D',
        16: 'B',
        17: '#',
        18: '$',
        19: '&',
        20: '@',
        21: '%',
        22: '^',
        23: '(',
        24: ')',
        25: '[',
        26: ']',
        27: '{',
        28: '}',
        29: '<',
        30: '>',
        31: '_',
        32: '"',
        33: "'",
        34: '`',
        35: ' ',
        36: '.',
        37: ',',
        38: ':',
        39: ';',
        40: '-',
        41: '~',
        42: '=',
        43: '|',
        44: '+',
        45: '*',
        46: '?',
        47: '!',
        48: '/',
        49: '\\',
        50: 'i',
        51: 'l',
        52: 't',
        53: 'v',
        54: 'x',
        55: 'r',
        56: 'c',
        57: 'o',
        58: 'f',
        59: 'j',
        60: 'u',
        61: 'n',
        62: 'x',
        63: 'k',
        64: 'h',
        65: 'a',
        66: 'e',
        67: 'y',
        68: 'z',
        69: 'm',
        70: 'w',
        71: 'g',
        72: 'p',
        73: 'q',
        74: 'd',
        75: 'b',
        76: 'R',
        77: 'H',
        78: 'S',
        79: 'G',
        80: 'F',
        81: 'T',
        82: 'C',
        83: 'L',
        84: 'W',
        85: 'E',
        86: 'Y',
        87: 'X',
        88: 'U',
        89: 'A',
        90: 'Z',
        91: 'M',
        92: 'Q',
        93: 'O',
        94: 'N',
        95: 'D',
        96: 'B',
        97: '#',
        98: '$',
        99: '&',
        100: '@',
        101: '%',
        102: '^',
        103: '(',
        104: ')',
        105: '[',
        106: ']',
        107: '{',
        108: '}',
        109: '<',
        110: '>',
        111: '_',
        112: '"',
        113: "'",
        114: '`',
        115: ' ',
        116: '.',
        117: ',',
        118: ':',
        119: ';',
        120: '-',
        121: '~',
        122: '=',
        123: '|',
        124: '+',
        125: '*',
        126: '?',
        127: '!'
    }


    # Reverse the dictionary


    # Open the image and resize it
    img = Image.open(image_path)
    width, height = img.size
    new_width = width * 4
    new_height = height * 4
    img = img.resize((new_width, new_height))

    # Convert the image to grayscale
    img = img.convert("L")

    # Get the pixel data
    pixels = np.array(img)

    # Create a new image with the same size as the original image
    new_img = Image.new("RGB", (new_width, new_height), color="white")
    draw = ImageDraw.Draw(new_img)

    # Generate the ASCII picture
    # caracter will take 4x4 pixel
    for y in range(0, new_height, 6):
        for x in range(0, new_width, 6):
            # Get the average brightness of the 3x3 pixel square
            avg_brightness = np.mean(pixels[y:y + 6, x:x + 6])

            # Get the ASCII character that best represents the average brightness
            brightness = math.ceil(avg_brightness / 5)
            ascii_char = caracter_brightness[brightness]

            # Draw the ASCII character on the new image
            draw.text((x, y), ascii_char, fill="black", spacing=60)

    # Save the ASCII picture and resize it to 500px height
    new_img = new_img.resize((math.floor(500 * new_width / new_height), 500))

    new_img.save("picture/ascii_artwork.jpg")


def get_random_artwork(xapp_token, api_url):
    try:
        url = api_url + 'artworks?offset=' + str(random.randint(0, 10000)) + '&size=1&page=1'
        response = requests.get(url, headers={"X-Api-Key": xapp_token})
        if response.status_code == 200:
            artwork = response.json()

            # Get the title of the artwork
            title = artwork["_embedded"]["artworks"][0]["title"]
            date = artwork["_embedded"]["artworks"][0]["date"]
            if date == "":
                date = "Unknown"
            rights = artwork["_embedded"]["artworks"][0]["image_rights"]
            medium = artwork["_embedded"]["artworks"][0]["medium"]
            if medium == "":
                medium = "Unknown"
            category = artwork["_embedded"]["artworks"][0]["category"]
            if category == "":
                category = "Unknown"

            print("category", category)

            # Get the image URL and download the image
            image_url = artwork["_embedded"]["artworks"][0]["_links"]["image"]["href"]
            image_url = image_url.replace("{image_version}", "large")

            # Download the image in /picture folder
            # If folder contains the image, it will be overwritten
            if os.path.exists("picture/artwork.jpg"):
                os.remove("picture/artwork.jpg")
            image = requests.get(image_url)

            with open("picture/artwork.jpg", "wb") as f:
                f.write(image.content)
            # resize the image to 500px height
            img = Image.open("picture/artwork.jpg")
            width, height = img.size
            new_image_width = math.floor(500 * width / height)
            img = img.resize((new_image_width, 500))
            img.save("picture/artwork.jpg")

            # Generate emoji square picture for the README
            generate_ascii_picture("picture/artwork.jpg")

            print("Downloaded image to /picture/artwork.jpg")

            if os.path.exists("README.md"):
                os.remove("README.md")

            # duplicate the template.md file to README.md and replace the {{ title }} and {{ date }} with the actual values
            with open("template.md", "r") as f:
                template = f.read()

                template = template.replace("{{ name }}", title)
                template = template.replace("{{ date }}", date)
                template = template.replace("{{ picture_rights }}", rights)
                template = template.replace("{{ medium }}", medium)
                template = template.replace("{{ category }}", category)

                with open("README.md", "w") as f:
                    f.write(template)
        else:
            print("Failed to fetch artwork. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


get_random_artwork(fetch_xapp_token(client_id, client_secret, api_url), api_url)
