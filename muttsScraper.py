import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  # Larger window size
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=options)

def get_better_quality_url(url):
    """Convert image URL to get a better quality version."""
    if '?' in url:
        base_url = url.split('?')[0]
        return f"{base_url}?width=1800&height=1800"
    return url

def download_image(image_url, folder, filename):
    """Download an image from a URL to a specified folder with a filename."""
    try:
        # Try to get a better quality version
        better_url = get_better_quality_url(image_url)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://mutts.com/"
        }
        
        response = requests.get(better_url, stream=True, headers=headers)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                filepath = os.path.join(folder, filename)
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(8192):
                        file.write(chunk)
                print(f"Downloaded: {filename}")
            else:
                print(f"Skipped: {filename} (Invalid Content-Type: {content_type})")
        else:
            print(f"Failed to download: {better_url} (Status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")

def scrape_mutts_comics(base_url, output_folder):
    """Scrape all comics from the MUTTS website using Selenium."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    driver = setup_driver()
    total = 1
    try:
        driver.get(base_url)
        page_num = 1
        
        while True:
            print(f"Processing page {page_num}")
            
            # Wait for the images to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "boost-sd__product-image-img"))
                )
                # Additional wait for images to fully load
                time.sleep(3)
            except TimeoutException:
                print("Timeout waiting for images to load")
                break

            # Find and process all comic images on the current page
            comics = driver.find_elements(By.CLASS_NAME, "boost-sd__product-image-img")
            print(f"Found {len(comics)} images on page {page_num}")
            
            for comic in comics:
                try:
                    image_url = comic.get_attribute('src')
                    if image_url:
                        filename = f"{total}_mutts.png"
                        total = total + 1
                        download_image(image_url, output_folder, filename)
                except Exception as e:
                    print(f"Error processing comic: {e}")
            
            # Try to find and click the next page button
            try:
                next_button = driver.find_element(By.CLASS_NAME, "boost-sd__pagination-button--next")
                if "disabled" in next_button.get_attribute("class"):
                    print("Reached the last page")
                    break
                next_button.click()
                time.sleep(3)  # Wait longer for page load
                page_num += 1
            except NoSuchElementException:
                print("No more pages found")
                break
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
                
    finally:
        driver.quit()

if __name__ == "__main__":
    base_url = "https://mutts.com/collections/comic-strips?sort=created-ascending"
    output_folder = "mutts_comics"
    scrape_mutts_comics(base_url, output_folder)