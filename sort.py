import os
import re
import shutil

source_dir = "./mnt"          # The directory containing *comics subfolders
destination_dir = "./sorted"  # Where to place sorted folders

# Regex to match files like "4_babyblues.png" where "4" is Y and "babyblues" is the comic name
pattern = re.compile(r"^(\d+)_(.+)\.png$", re.IGNORECASE)

files_by_y = {}

# Walk the source directory and find files
for root, dirs, files in os.walk(source_dir):
    for fname in files:
        match = pattern.match(fname)
        if match:
            y_str, comic_name = match.groups()
            y_val = int(y_str)
            file_path = os.path.join(root, fname)
            # Group files by Y
            files_by_y.setdefault(y_val, []).append(file_path)

# Now create a single folder per Y and copy all files there
for y_val, file_list in files_by_y.items():
    # Folder named after Y
    out_folder = os.path.join(destination_dir, str(y_val))
    os.makedirs(out_folder, exist_ok=True)

    for fpath in file_list:
        dest_path = os.path.join(out_folder, os.path.basename(fpath))
        print(f"Copying {fpath} -> {dest_path}")
        shutil.copy(fpath, dest_path)

print("Copying complete.")
