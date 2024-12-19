from waveshare_epd import epd7in5_V2
from PIL import Image, ImageEnhance, ImageFilter
import time

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
            # print("hello")
            img = self._apply_dithering(img)
        else:
            # Process for 4-gray display
            img = self._process_4gray(img)
        
        return img
    def _resize_image(self, img, target_width, target_height):
        # Calculate aspect ratios
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        # Create a white background of target size
        white_bg = Image.new('L', (target_width, target_height), 255)  # '255' for white background
        
        if img_ratio > target_ratio:
            # Image is wider than target - fit to width
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller than target - fit to height
            new_width = int(target_height * img_ratio)
            new_height = target_height
        
        # Resize the image while maintaining aspect ratio
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Calculate position to center the image on the white background
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Paste the resized image onto the white background
        white_bg.paste(img, (x_offset, y_offset))
        
        return white_bg
    # def _resize_image(self, img, target_width, target_height):
    #     # Calculate aspect ratios
    #     img_ratio = img.width / img.height
    #     target_ratio = target_width / target_height
        
    #     if img_ratio < target_ratio:
    #         # Image is wider - crop the sides
    #         new_width = int(img.height * target_ratio)
    #         offset = (img.width - new_width) // 2
    #         img = img.crop((offset, 0, offset + new_width, img.width))
    #     elif img_ratio > target_ratio:
    #         # Image is taller - crop the top/bottom
    #         new_height = int(img.width / target_ratio)
    #         offset = (img.height - new_height) // 2
    #         img = img.crop((0, offset, img.height, offset + new_height))
            
    #     # Resize using high-quality Lanczos resampling
    #     return img.resize((target_width, target_height), Image.LANCZOS)
    
    def _enhance_image(self, img):
        # Apply a series of careful enhancements
        img = ImageEnhance.Contrast(img).enhance(1.4)  # Slightly increased contrast
        img = ImageEnhance.Brightness(img).enhance(1.2)  # Subtle brightness boost
        img = ImageEnhance.Sharpness(img).enhance(1.4)  # Moderate sharpening
        
        # Adjust gamma to improve midtones
        gamma = 1.1
        gamma_table = [int((i / 255) ** gamma * 255) for i in range(256)]
        return img.point(gamma_table)
    def _process_4gray(self, img):
        # Convert to 4 levels of gray using an 8x8 Bayer matrix for better resolution
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
        
        # Normalize the threshold map to match our grayscale range
        threshold_map = [int(t * (255/64)) for t in threshold_map]
        
        width, height = img.size
        pixels = img.load()
        
        # Create a new image for 4-gray output
        output_img = Image.new('L', (width, height))
        output_pixels = output_img.load()
        
        for y in range(height):
            for x in range(width):
                old_pixel = pixels[x, y]
                # Use 8x8 matrix for finer dithering
                threshold = threshold_map[(x % 8) + (y % 8) * 8]
                
                # Apply threshold with error diffusion
                adjusted_pixel = old_pixel + (old_pixel - threshold) * 0.2
                
                # Determine which of the 4 gray levels to use with smoother transitions
                if adjusted_pixel > 220:    # Expanded white range
                    new_pixel = 255        # Pure white
                elif adjusted_pixel > 165:  # Light gray range
                    new_pixel = 170
                elif adjusted_pixel > 90:   # Dark gray range
                    new_pixel = 85
                else:                      # Black range
                    new_pixel = 0
                
                output_pixels[x, y] = new_pixel
                
        return output_img

    
    def _apply_dithering(self, img):
        # Standard binary dithering for 2-color mode
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    def display_image(self, image_path):
        
        final_image = self.enhance_and_fit_image(image_path)
        
        if self.use_4gray:
            self.epd.display_4Gray(self.epd.getbuffer_4Gray(final_image))
        else:
            self.epd.display(self.epd.getbuffer(final_image))
            
        final_image.save("processed_" + image_path)  # Save processed version for comparison
        time.sleep(5)
             
    def clear(self):
        if self.use_4gray:
            # Create a pure white image
            white_image = Image.new('L', (self.epd.width, self.epd.height), 255)
            self.epd.display_4Gray(self.epd.getbuffer_4Gray(white_image))
        else:
            self.epd.Clear()

# Usage example
# Initialize with 4-gray mode enabled
processor = EinkImageProcessor(use_4gray=True)

# Display image
processor.display_image("daily_comic_1.png")
processor.clear()
processor.display_image("sunday_comic_7.png")
processor.clear()
processor.epd.sleep()


