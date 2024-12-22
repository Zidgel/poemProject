import time
import os
import logging
from pathlib import Path
from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from waveshare_epd import epd7in5_V2

class EPaperDisplay:
    """Controls a Waveshare 7.5inch V2 E-Paper display."""
    
    DEFAULT_FONT_SIZE = 24
    DEFAULT_UPDATE_INTERVAL = 20  # seconds
    
    def __init__(self, use_4gray: bool = True):
        """
        Initialize the E-Paper display.
        
        Args:
            use_4gray: Whether to use 4-level grayscale mode (True) or binary mode (False)
        """
        self.logger = logging.getLogger(__name__)
        self.use_4gray = use_4gray
        
        try:
            self.epd = epd7in5_V2.EPD()
            self.init_display()
        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            raise
            
        # Cache display dimensions
        self.width = self.epd.width
        self.height = self.epd.height
        
    def init_display(self) -> None:
        """Initialize the display with appropriate mode."""
        self.epd.init()
        if self.use_4gray:
            self.logger.info("Initializing in 4-gray mode")
            self.epd.init_4Gray()
        
    def enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply image enhancements for better display quality."""
        img = img.convert('L')
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Enhance contrast, brightness, and sharpness
        enhancements = [
            (ImageEnhance.Contrast, 1.4),
            (ImageEnhance.Brightness, 1.2),
            (ImageEnhance.Sharpness, 1.4)
        ]
        
        for enhancer_class, factor in enhancements:
            img = enhancer_class(img).enhance(factor)
            
        # Apply gamma correction
        gamma = 1.1
        gamma_table = [int((i / 255) ** gamma * 255) for i in range(256)]
        return img.point(gamma_table)
    
    def process_grayscale(self, img: Image.Image) -> Image.Image:
        """Process image for 4-level grayscale display."""
        width, height = img.size
        pixels = img.load()
        output_img = Image.new('L', (width, height))
        output_pixels = output_img.load()
        
        # Optimized dithering matrix
        threshold_matrix = [
            [0, 48, 12, 60], [32, 16, 44, 28],
            [8, 56, 4, 52], [40, 24, 36, 20]
        ]
        
        matrix_size = 4
        for y in range(height):
            for x in range(width):
                old_pixel = pixels[x, y]
                matrix_x = x % matrix_size
                matrix_y = y % matrix_size
                threshold = threshold_matrix[matrix_y][matrix_x] * 4
                
                # Apply error diffusion
                if old_pixel > 220:
                    new_pixel = 255
                elif old_pixel > 165:
                    new_pixel = 170
                elif old_pixel > 90:
                    new_pixel = 85
                else:
                    new_pixel = 0
                    
                output_pixels[x, y] = new_pixel
                
        return output_img
    
    def prepare_image(self, img: Image.Image) -> Image.Image:
        """Prepare image for display with appropriate processing."""
        img = self.enhance_image(img)
        if self.use_4gray:
            return self.process_grayscale(img)
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    def display_image(self, image: Union[str, Image.Image, Path]) -> None:
        """Display an image on the E-Paper display."""
        try:
            if isinstance(image, (str, Path)):
                img = Image.open(image)
            else:
                img = image
                
            img = self.prepare_image(img)
            
            if self.use_4gray:
                self.epd.display_4Gray(self.epd.getbuffer_4Gray(img))
            else:
                self.epd.display(self.epd.getbuffer(img))
                
        except Exception as e:
            self.logger.error(f"Failed to display image: {e}")
            raise
            
    def create_text_image(self, 
                         text: str, 
                         font_path: Optional[str] = None, 
                         font_size: int = DEFAULT_FONT_SIZE) -> Image.Image:
        """Create an image from text with proper formatting."""
        img = Image.new('L', (self.width, self.height), 255)
        draw = ImageDraw.Draw(img)
        
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            self.logger.warning(f"Failed to load font {font_path}, using default: {e}")
            font = ImageFont.load_default()
            
        # Calculate text wrapping
        avg_char_width = font.getlength("x")
        max_chars = int(self.width / avg_char_width * 0.95)  # 95% of width
        
        # Process text with proper line breaks
        lines = []
        y_position = 10
        
        for paragraph in text.split('\n'):
            words = paragraph.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                if current_length + word_length + 1 <= max_chars:
                    current_line.append(word)
                    current_length += word_length + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length + 1
                    
            if current_line:
                lines.append(' '.join(current_line))
            lines.append('')  # Add paragraph break
            
        # Draw text
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x_position = (self.width - line_width) // 2
            
            draw.text((x_position, y_position), line, font=font, fill=0)
            y_position += bbox[3] - bbox[1] + 5  # Add 5px line spacing
            
        return img
    
    def clear(self) -> None:
        """Clear the display."""
        try:
            if self.use_4gray:
                white_image = Image.new('L', (self.width, self.height), 255)
                self.epd.display_4Gray(self.epd.getbuffer_4Gray(white_image))
            else:
                self.epd.Clear()
        except Exception as e:
            self.logger.error(f"Failed to clear display: {e}")
            raise
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper cleanup when used as context manager."""
        try:
            self.clear()
            self.epd.sleep()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    text_file = Path("A_CHARACTER.txt")
    
    try:
        with EPaperDisplay(use_4gray=False) as display:
            while True:
                try:
                    text = text_file.read_text(encoding='utf-8')
                except FileNotFoundError:
                    logger.error(f"File not found: {text_file}")
                    text = "File not found: Please create A_CHARACTER.txt"
                except Exception as e:
                    logger.error(f"Error reading file: {e}")
                    text = f"Error reading file: {str(e)}"
                
                text_image = display.create_text_image(text)
                display.display_image(text_image)
                
                time.sleep(EPaperDisplay.DEFAULT_UPDATE_INTERVAL)
                
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()