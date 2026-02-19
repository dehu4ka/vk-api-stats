import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
BASE_URL = "https://lk-b2b.camera.rt.ru/api"
AUTH_HEADER = f"Bearer token={API_KEY}"

CACHE_TTL_CAMERAS = 60
CACHE_TTL_STATS = 120
CACHE_TTL_ARCHIVES = 300
CACHE_TTL_FRAGMENTS = 600
CACHE_TTL_HEALTH = 30

PER_PAGE = 1000
