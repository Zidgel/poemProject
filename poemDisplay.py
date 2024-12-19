import time
import os
from waveshare_epd import epd7in5_V2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
from textwrap import wrap

base_folder = "/comic_strips"  # Not used now, but keeping for reference
display_interval = 20  # Time in seconds between updates
text_file = "A_CHARACTER.txt"  # The text file you want to display

class EinkImageProcessor:
    def __init__(self, use_4gray=True):
        self.epd = epd7in5_V2.EPD()
        self.use_4gray = use_4gray
        self.epd.init()
        if use_4gray:
            print("Use 4Gray")
            self.epd.init_4Gray()
        
    def enhance_and_fit_image(self, image_path):
        # Load the image
        img = Image.open(image_path)
        screen_width, screen_height = self.epd.width, self.epd.height
        
        # Convert to grayscale with enhanced bit depth
        img = img.convert('L')
        
        # Apply subtle Gaussian blur to reduce noise before processing
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Resize with high-quality algorithm
        img = self._resize_image(img, screen_width, screen_height)
        
        # Enhance image
        img = self._enhance_image(img)
        
        if not self.use_4gray:
            # Apply binary dithering for 2-color mode
            img = self._apply_dithering(img)
        else:
            # Process for 4-gray display
            img = self._process_4gray(img)
        
        return img

    def _resize_image(self, img, target_width, target_height):
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        white_bg = Image.new('L', (target_width, target_height), 255)
        
        if img_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            new_width = int(target_height * img_ratio)
            new_height = target_height
        
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        white_bg.paste(img, (x_offset, y_offset))
        
        return white_bg

    def _enhance_image(self, img):
        img = ImageEnhance.Contrast(img).enhance(1.4)
        img = ImageEnhance.Brightness(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.4)
        
        gamma = 1.1
        gamma_table = [int((i / 255) ** gamma * 255) for i in range(256)]
        return img.point(gamma_table)

    def _process_4gray(self, img):
        threshold_map = [
            0,  48, 12, 60,  3, 51, 15, 63,
            32, 16, 44, 28, 35, 19, 47, 31,
            8,  56,  4, 52, 11, 59,  7, 55,
            40, 24, 36, 20, 43, 27, 39, 23,
            2,  50, 14, 62,  1, 49, 13, 61,
            34, 18, 46, 30, 33, 17, 45, 29,
            10, 58,  6, 54,  9, 57,  5, 53,
            42, 26, 38, 22, 41, 25, 37, 21
        ]
        threshold_map = [int(t * (255/64)) for t in threshold_map]
        
        width, height = img.size
        pixels = img.load()
        
        output_img = Image.new('L', (width, height))
        output_pixels = output_img.load()
        
        for y in range(height):
            for x in range(width):
                old_pixel = pixels[x, y]
                threshold = threshold_map[(x % 8) + (y % 8) * 8]
                adjusted_pixel = old_pixel + (old_pixel - threshold) * 0.2
                if adjusted_pixel > 220:
                    new_pixel = 255
                elif adjusted_pixel > 165:
                    new_pixel = 170
                elif adjusted_pixel > 90:
                    new_pixel = 85
                else:
                    new_pixel = 0
                
                output_pixels[x, y] = new_pixel
                
        return output_img

    def _apply_dithering(self, img):
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    def display_image(self, image_path):
        final_image = self.enhance_and_fit_image(image_path)
        
        if self.use_4gray:
            self.epd.display_4Gray(self.epd.getbuffer_4Gray(final_image))
        else:
            self.epd.display(self.epd.getbuffer(final_image))
            
        final_image.save("processed_" + os.path.basename(image_path))  
        time.sleep(5)
             
    def clear(self):
        if self.use_4gray:
            white_image = Image.new('L', (self.epd.width, self.epd.height), 255)
            self.epd.display_4Gray(self.epd.getbuffer_4Gray(white_image))
        else:
            self.epd.Clear()

def create_image_from_text(text, width, height, font_path=None, font_size=24):
    """
    Create a white-background image of the specified width and height,
    with the given text drawn onto it.

    Uses word wrapping to fit text within the image.
    """
    img = Image.new('L', (width, height), 255)  # White background
    draw = ImageDraw.Draw(img)

    # Load a font (Adjust path as needed)
    # If you don't have a TTF font, omit font_path to use a default PIL font
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()

    # Word wrap the text to fit in the given width
    max_width = width - 20  # Some padding
    lines = []
    for paragraph in text.split('\n'):
        wrapped = wrap(paragraph, width=40)  # Adjust as needed
        lines.extend(wrapped if wrapped else [''])

    # Draw the text line by line
    y_text = 10
    for line in lines:
        w, h = draw.textsize(line, font=font)
        # If line too wide, you can dynamically wrap based on textsize if needed
        draw.text(((width - w) / 2, y_text), line, font=font, fill=0)  # '0' for black text
        y_text += h + 5

    return img

def main():
    processor = EinkImageProcessor(use_4gray=False)
    
    # Get the screen dimensions from the processor epd
    screen_width, screen_height = processor.epd.width, processor.epd.height

    while True:
        # Read text from the text file
        if os.path.exists(text_file):
            with open(text_file, 'r') as f:
                content = f.read()
        else:
            content = "No text file found."

        # Create an image from the text
        text_img = create_image_from_text(content, screen_width, screen_height, font_path=None, font_size=24)

        # Save this text image as a temporary file
        temp_image_path = "text_display.png"
        text_img.save(temp_image_path)

        # Display the generated image
        processor.display_image(temp_image_path)

        time.sleep(display_interval)
        processor.clear()

        print("Waiting for the next update...")
        time.sleep(5)  # Check every 5 seconds for new text

if __name__ == "__main__":
    main()
