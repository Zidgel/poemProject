
from PyPDF2 import PdfReader

from PIL import Image

import fitz  # PyMuPDF

import os



# Define file path

pdf_path = "./mnt/c+h.pdf"

output_dir = "./mnt/calvin_hobbes_comics"

# Create output directory if it doesn't exist

os.makedirs(output_dir, exist_ok=True)



# Open the PDF

pdf_document = fitz.open(pdf_path)

# Process each page
comic_count = 0
for page_number in range(1351):

    page = pdf_document[page_number]

    pix = page.get_pixmap()
    page_width = pix.width -17
    page_height = (pix.height // 5)   # Each comic is one-third of the page height

    # Save Sunday comics as a single file

    if (page_number+1) % 3 == 0:  # Assuming Sunday comics are on every 7th page starting from the first
        comic_count += 1
        # print("Sunday PAGENumber", page_number)

        rect = fitz.Rect(x0=9, y0=170, x1=pix.width-10, y1=605)
        print(f"Rect: x0={rect.x0}, y0={rect.y0}, x1={rect.x1}, y1={rect.y1}")

        comic_pix = page.get_pixmap(clip=rect)
        output_path = os.path.join(output_dir, f"{comic_count}_ch.png")
        comic_pix.save(output_path)

        print(f"Saved: {output_path}")

    else:  # Save daily comics individually
        print("Daily PAGENumber", page_number)
        
        
        
        for comic_index in range(3):  # Extract 3 comics per page
            comic_count += 1
            # Define the rectangle for each comic
            if comic_index == 0:
                rect = fitz.Rect(x0=25, y0=(comic_index+1) * page_height - 80, x1=page_width, y1=(comic_index+2) * page_height-50)
            
            elif comic_index == 1:
                rect = fitz.Rect(x0=25, y0=(comic_index+1) * page_height - 20, x1=page_width, y1=(comic_index+2) * page_height + 5)

            else:
                rect = fitz.Rect(x0=25, y0=(comic_index+1) * page_height + 35, x1=page_width, y1=(comic_index+2) * page_height+60)

            comic_pix = page.get_pixmap(clip=rect)  # Extract only this section

            # Save the extracted comic
            output_path = os.path.join(output_dir, f"{comic_count}_ch.png")
            comic_pix.save(output_path)
            print(f"Saved: {output_path}")

