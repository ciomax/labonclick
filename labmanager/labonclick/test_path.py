from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

print(BASE_DIR)
media_dir = BASE_DIR.joinpath('media')
print(media_dir)
