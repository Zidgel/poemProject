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
#bignate/1991/01/07
#frazz/2001/04/02
#foxtrot/2006/01/02

def download_lio_comic(date_obj, output_folder, total, comic):
    """
    Download the Lio comic for the given date (datetime object) into the specified folder.
    Returns True if successful, False if comic not found or error occurs.
    """

    url = f"https://www.gocomics.com/{comic}/{date_obj.year}/{date_obj.month:02d}/{date_obj.day:02d}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to load page for {date_obj.strftime('%Y-%m-%d')}, status: {response.status_code}")
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    comic_img = soup.select_one("picture.item-comic-image img")

    if not comic_img:
        print(f"No comic image found on {date_obj.strftime('%Y-%m-%d')}")
        return False

    image_url = comic_img.get("src")
    alt_text = comic_img.get("alt", "")

    if not image_url:
        print(f"No image URL found on {date_obj.strftime('%Y-%m-%d')}")
        return False

    # Format date for the filename, e.g. "2006-05-15"
    filename = f"{total}_{comic}.png"
 
    filepath = os.path.join(output_folder, filename)

    img_response = requests.get(image_url, headers=headers)
    if img_response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(img_response.content)
        print(f"{date_obj} Downloaded comic for {total} as {filename}")
        return True
    else:
        print(f"Failed to download image for {total}, status: {img_response.status_code}")
        return False

# Configuration
comic = "lio"
output_folder = f"{comic}_comics"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# lio/2006/05/15
# Set a start and end date to scrape
start_date = datetime(2006, 5, 15) 
end_date = datetime(2024, 12, 18)  # For example, 5 days from start date

current_date = start_date
total = 1
while current_date <= end_date:
    
    download_lio_comic(current_date, output_folder, total, comic)
    total = total + 1
    current_date += timedelta(days=1)
