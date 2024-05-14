import sys, random, argparse, requests, os
import numpy as np
import math
from PIL import Image

# Define the API URL
api_url = "https://api.artsy.net/api/"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def fetch_xapp_token(client_id, client_secret, api_url):
    try:
        response = requests.post(api_url+'tokens/xapp_token', json={"client_id": client_id, "client_secret": client_secret})
        if response.status_code == 201:
            xapp_token = response.json().get("token")
            return xapp_token
        else:
            print("Failed to fetch xapp token. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None



def get_random_artwork(xapp_token, api_url):
    try:
        url = api_url+'artworks?offset='+str(random.randint(0, 10000))+'&size=1&page=1'
        response = requests.get(url, headers={"X-Api-Key": xapp_token})
        if response.status_code == 200:
            artwork = response.json()

            # Get the title of the artwork
            title = artwork["_embedded"]["artworks"][0]["title"]
            date =   artwork["_embedded"]["artworks"][0]["date"]
            if date == "":
                date = "Unknown"
            rights = artwork["_embedded"]["artworks"][0]["image_rights"]
            medium = artwork["_embedded"]["artworks"][0]["medium"]
            if medium == "":
                medium = "Unknown"
            category = artwork["_embedded"]["artworks"][0]["category"]
            if category == "":
                category = "Unknown"

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
            new_width = math.floor(500 * width / height)
            img = img.resize((new_width, 500))
            img.save("picture/artwork.jpg")

            print("Downloaded image to /picture/artwork.jpg")

            if os.path.exists("README.md"):
                os.remove("README.md")

            # duplicate the template.md file to README.md and replace the {{ title }} and {{ date }} with the actual values
            with open("template.md", "r") as f:
                template = f.read()
                # {{ name }}
                # {{ date }}

                # {{ picture_rights }}
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