import os
import zipfile

BEED_DIR = "data/Beed"

def is_zip_file(path):
    with open(path, "rb") as f:
        return f.read(2) == b"PK"

for fname in os.listdir(BEED_DIR):
    fpath = os.path.join(BEED_DIR, fname)

    # only .nc files
    if not fname.lower().endswith(".nc"):
        continue

    # skip real NetCDF files
    if not is_zip_file(fpath):
        continue

    extract_dir = fpath.replace(".nc", "")
    os.makedirs(extract_dir, exist_ok=True)

    print(f"Unzipping: {fname}")

    with zipfile.ZipFile(fpath, "r") as z:
        z.extractall(extract_dir)

    # OPTIONAL cleanup (do later if you want)
    # os.remove(fpath)
