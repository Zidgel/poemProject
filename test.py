from waveshare_epd import epd7in5_V2  # Import the correct driver for your eInk display
from PIL import Image, ImageEnhance
import time
# Initialize eInk display
epd = epd7in5_V2.EPD()
epd.init()
# epd.init_4Gray()
epd.Clear()

def enhance_and_fit_image(image_path):
    # Load the image
    img = Image.open(image_path)

    # Get the eInk display resolution
    screen_width, screen_height = epd.width, epd.height
    screen_aspect_ratio = screen_width / screen_height

    # Convert the image to grayscale
    img = img.convert("L")  # Grayscale mode

    # Get the image dimensions and aspect ratio
    img_width, img_height = img.size
    img_aspect_ratio = img_width / img_height

    # Determine whether to crop or pad the image
    if img_aspect_ratio < screen_aspect_ratio:
        # Image is wider than the screen; crop width
        print("TOO WIDE: Cropping width to match screen aspect ratio.")
        new_width = int(img_height * screen_aspect_ratio)
        offset = (img_width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img_height))
    elif img_aspect_ratio > screen_aspect_ratio:
        # Image is taller than the screen; crop height
        print("TOO TALL: Cropping height to match screen aspect ratio.")
        new_height = int(img_width / screen_aspect_ratio)
        offset = (img_height - new_height) // 2
        img = img.crop((0, offset, img_width, offset + new_height))
    else:
        print("PERFECT FIT: No cropping needed.")

    # Resize the image to the display resolution
    img = img.resize((epd.width, epd.height), Image.LANCZOS)

    # If the aspect ratio was preserved but padding is needed, ensure the image fits
    canvas = Image.new("L", (epd.width, epd.height), 255)  # White background
    canvas.paste(img, (0, 0))  # Paste the resized image onto the canvas

    img = ImageEnhance.Contrast(img).enhance(1.3)  # Boost contrast moderately
    img = ImageEnhance.Sharpness(img).enhance(1.2)  # Sharpen the image moderately


    # Apply dithering for better quality on the eInk display
    # img = canvas.convert("1", dither=Image.FLOYDSTEINBERG)
    img.save("processed_image.png")

    return img


# Path to your image
image_path = "daily_comic_1.png" #"daily_comic_1.png" "sunday_comic_7.png"

# Enhance and center the image
final_image = enhance_and_fit_image(image_path)
#  mode=epd.PARTIAL_UPDATE

# epd.getbuffer_4Gray
# epd.display_4Gray
# Display the image on the eInk
epd.display(epd.getbuffer(final_image))
time.sleep(5)
epd.Clear()
epd.sleep()
