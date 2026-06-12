import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "amz_data_pet_research/1.0")

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DATA_EXPORTS = ROOT_DIR / "data" / "exports"

# Pet Supplies category config
PET_SUPPLIES_CATEGORY_ID = 2975312011
PET_SUPPLIES_SEARCH_TERMS = [
    "dog food", "dog treats", "dog toys", "dog bed",
    "cat food", "cat litter", "cat toys", "cat tree",
    "pet camera", "pet feeder", "pet fountain", "pet gate",
    "dog leash", "dog collar", "dog grooming",
    "aquarium", "bird cage", "small animal cage",
]

# Ensure data directories exist
for d in [DATA_RAW, DATA_PROCESSED, DATA_EXPORTS]:
    d.mkdir(parents=True, exist_ok=True)
