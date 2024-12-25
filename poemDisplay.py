import time
import logging
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in5_V2

class EpaperDisplay:
    def __init__(self):
        self.epd = epd7in5_V2.EPD()
        self.epd.init()
        
    def create_text_image(self, text):
        # Create image in portrait orientation
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Path to TTF font
        font_size = 16  # Adjust this for desired size
        font = ImageFont.truetype(font_path, font_size)

        # Text layout parameters
        x_pos = 20
        y_pos = 20
        line_height = font_size + 4

        # Ensure lines are wrapped at 54 characters
        wrapped_text = []
        lineLength = 50
        for line in text:
            line = line.expandtabs(4)
            while len(line) > lineLength:
                # Find the last space/comma/period within the limit
                split_index = max(line.rfind(" ", 0, lineLength), line.rfind(",", 0, lineLength), line.rfind(".", 0, lineLength))
                if split_index == -1:  # If no space/comma/period is found, split at the limit
                    split_index = lineLength
                wrapped_text.append(line[:split_index + 1])  # Include the split character
                line = line[split_index + 1:].lstrip()  # Remove the processed part and leading spaces
            wrapped_text.append(line)  # Add the remaining part of the line

        # Draw each line on the display
        for line in wrapped_text:
            draw.text((x_pos, y_pos), line, font=font, fill=0)
            y_pos += line_height  # Move to the next line

        return image.rotate(90, expand=True)
    
    def display_text(self, lines):
        try:
            image = self.create_text_image(lines)
            self.epd.display(self.epd.getbuffer(image))
        except Exception as e:
            logging.error(f"Display error: {e}")
            
    def clear(self):
        self.epd.Clear()
        
    def sleep(self):
        self.epd.sleep()

def main():
    logging.basicConfig(level=logging.INFO)
    display = EpaperDisplay()

    try:
        for _ in range(2): ##TODO
            try:
                # Get a random poem file from the "poems" folder
                poem_folder = Path("poems")
                poem_files = list(poem_folder.glob("*.txt"))
                if not poem_files:
                    display.display_text(["No poems found in the folder."])
                    break

                selected_poem = random.choice(poem_files)
                text = selected_poem.read_text().strip()

                # Split the text into lines
                lines = text.split("\n")

                # Define chunk parameters
                chunk_size = 30
                chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
                totalTime = 600 ##TODO
                perPage = 30 ##TODO
                # Cycle through the chunks for 10 minutes
                start_time = time.time()
                while time.time() - start_time < totalTime:  # 10 minutes
                    if len(chunks) == 1:
                        print("ONE PROSE")
                        # If the poem fits on the screen, display it once and wait
                        display.display_text(chunks[0])
                        time.sleep(totalTime - (time.time() - start_time))
                        break
                    else:
                        print("Multiprose")
                        for chunk in chunks:
                            display.display_text(chunk)
                            time.sleep(perPage)  # Display each chunk for 20 seconds
            
            except Exception as e:
                logging.error(f"Error: {e}")
                display.display_text([f"Error: {str(e)}"])
                break
    
    except KeyboardInterrupt:
        display.clear()
        display.sleep()

    finally:
        display.clear()
        display.sleep()

if __name__ == "__main__":
    main()
