import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
#lio/2006/05/15
#pearlsbeforeswine 2002/01/07
#wallace-the-brave/2015/07/06
#pickles/2003/01/01
#culdesac/2007/10/01
#poochcafe/2003/04/27
#frazz/2001/04/02
#sarahs-scribbles/2014/01/02
#babyblues/1990/01/07
#foxtrot/2006/01/ 02

# bignate/1991/01/07
def download_comic(url, output_folder, total, comic):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to load page {url}, status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    comic_img = soup.select_one("picture.item-comic-image img")

    if not comic_img:
        print(f"No comic image found at {url}")
        return None

    image_url = comic_img.get("src")
    if not image_url:
        print(f"No image URL found at {url}")
        return None

    filename = f"{total}_{comic}.png"
    filepath = os.path.join(output_folder, filename)

    img_response = requests.get(image_url, headers=headers)
    if img_response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(img_response.content)
        print(f"Downloaded comic #{total} from {url} as {filename}")
    else:
        print(f"Failed to download image from {image_url}, status: {img_response.status_code}")

    # Find the 'Next' button link
    next_link_tag = soup.select_one('a.fa-caret-right')
    if next_link_tag:
        next_url = next_link_tag.get('href')
        if next_url and not next_url.startswith('http'):
            next_url = "https://www.gocomics.com" + next_url
        return next_url
    else:
        # No next link found
        return None

# Configuration foxtrot/2006/01/02
comic = "bignate"
output_folder = f"{comic}_comics"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

start_url = "https://www.gocomics.com/bignate/1991/05/29"
current_url = start_url
total = 139

while current_url and total != 3151:
    current_url = download_comic(current_url, output_folder, total, comic)
    if current_url:
        total += 1
    else:
        print("No more comics found. Exiting loop.")
        break