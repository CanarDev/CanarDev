import random
import requests
import os
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont

# Define the API URL
API_URL = "https://api.artsy.net/api/"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CURRENT_USER_ID = os.environ.get("CURRENT_USER_ID")
USER_EMAIL = os.environ.get("USER_EMAIL")
USER_PASSWORD = os.environ.get("USER_PASSWORD")

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


def get_access_token():
    url = "https://api.artsy.net/oauth2/access_token"

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "credentials",
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    }

    response = requests.post(url, data=payload)

    if response.status_code == 201:
        print("Access token fetched")
        return response.json()["access_token"]
    else:
        response.raise_for_status()


def delete_access_token(access_token):
    url = API_URL + "tokens/access_token"

    headers = {
        "X-Access-Token": access_token
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("Access token deleted")
    else:
        response.raise_for_status()


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


def generate_ascii_picture(image_path):
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

    new_img = new_img.resize((math.floor(500 * new_width / new_height), 500))
    new_img.save("picture/ascii_artwork.jpg")


def save_artwork_artsy(artwork_id, access_token):
    try:
        print('TOKEN', access_token)
        response = requests.post("https://metaphysics-production.artsy.net/v2",
                                 headers={
                                     "content-type": "application/json",
                                     "x-access-token": access_token,
                                     "x-original-session-id": "7371bbe0-10a0-11ef-8591-c9cef036965c",
                                     "x-user-id": CURRENT_USER_ID
                                 },
                                 json={
                                     "id": "useSelectArtworkListsMutation",
                                     "query": "mutation useSelectArtworkListsMutation(\n  $input: ArtworksCollectionsBatchUpdateInput!\n) {\n  artworksCollectionsBatchUpdate(input: $input) {\n    responseOrError {\n      __typename\n      ... on ArtworksCollectionsBatchUpdateSuccess {\n        addedToArtworkLists: addedToCollections {\n          internalID\n          default\n          ...ArtworkListItem_item\n          id\n        }\n        removedFromArtworkLists: removedFromCollections {\n          internalID\n          default\n          ...ArtworkListItem_item\n          id\n        }\n      }\n      ... on ArtworksCollectionsBatchUpdateFailure {\n        mutationError {\n          statusCode\n        }\n      }\n    }\n  }\n}\n\nfragment ArtworkListItem_item on Collection {\n  default\n  name\n  internalID\n  artworksCount(onlyVisible: true)\n  shareableWithPartners\n  artworksConnection(first: 4) {\n    edges {\n      node {\n        image {\n          url(version: \"square\")\n        }\n        id\n      }\n    }\n  }\n}\n",
                                     "variables": {
                                         "input": {
                                             "artworkIDs": [
                                                 artwork_id
                                             ],
                                             "addToCollectionIDs": [
                                                 "50284c1c-ea80-4147-85d3-886361d22663"
                                             ]
                                         }
                                     }
                                 })
        if response.status_code == 200:
            print(response.json())
            print("Artwork saved to Artsy")

        else:
            print(response)
            print("Failed to save artwork to Artsy. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def get_random_artwork(xapp_token, api_url):
    try:
        url = api_url + 'artworks?offset=' + str(random.randint(0, 10000)) + '&size=1&page=1'
        response = requests.get(url, headers={"X-Api-Key": xapp_token})
        if response.status_code == 200:
            artwork = response.json()
            title = artwork["_embedded"]["artworks"][0]["title"]
            date = artwork["_embedded"]["artworks"][0]["date"] or "Unknown"
            rights = artwork["_embedded"]["artworks"][0]["image_rights"]
            medium = artwork["_embedded"]["artworks"][0]["medium"] or "Unknown"
            category = artwork["_embedded"]["artworks"][0]["category"] or "Unknown"
            art_link = artwork["_embedded"]["artworks"][0]["_links"]["permalink"]["href"]
            artwork_id = artwork["_embedded"]["artworks"][0]["id"]

            access_token = response.headers.get("X-Access-Token")
            print("access_token", access_token)

            print("category", category)
            print('id', artwork_id)
            print('xapp_token', xapp_token)
            print(artwork)

            image_url = artwork["_embedded"]["artworks"][0]["_links"]["image"]["href"]
            image_url = image_url.replace("{image_version}", "large")

            if os.path.exists("picture/artwork.jpg"):
                os.remove("picture/artwork.jpg")
            image = requests.get(image_url)

            with open("picture/artwork.jpg", "wb") as f:
                f.write(image.content)

            img = Image.open("picture/artwork.jpg")
            width, height = img.size
            new_image_width = math.floor(500 * width / height)
            img = img.resize((new_image_width, 500))
            img.save("picture/artwork.jpg")

            generate_ascii_picture("picture/artwork.jpg")

            print("Downloaded image to /picture/artwork.jpg")

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

            save_artwork_artsy(artwork_id, get_access_token())


        else:
            print("Failed to fetch artwork. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


# get_random_artwork(fetch_xapp_token(CLIENT_ID, CLIENT_SECRET, API_URL), API_URL)
get_access_token()

