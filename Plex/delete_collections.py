from alive_progress import alive_bar
from plexapi.server import PlexServer
import os
from dotenv import load_dotenv
import time

load_dotenv()

PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_TIMEOUT = os.getenv("PLEX_TIMEOUT")
LIBRARY_NAME = os.getenv("LIBRARY_NAME")
LIBRARY_NAMES = os.getenv("LIBRARY_NAMES")
DELAY = int(os.getenv("DELAY"))
KEEP_COLLECTIONS = os.getenv("KEEP_COLLECTIONS")

if not DELAY:
    DELAY = 0

if not PLEX_TIMEOUT:
    PLEX_TIMEOUT = 120

if LIBRARY_NAMES:
    lib_array = LIBRARY_NAMES.split(",")
else:
    lib_array = [LIBRARY_NAME]

if KEEP_COLLECTIONS:
    keeper_array = KEEP_COLLECTIONS.split(",")
else:
    keeper_array = [KEEP_COLLECTIONS]

os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(PLEX_TIMEOUT)

plex = PlexServer(PLEX_URL, PLEX_TOKEN)

coll_obj = {}
coll_obj["collections"] = {}


def get_sort_text(argument):
    switcher = {0: "release", 1: "alpha", 2: "custom"}
    return switcher.get(argument, "invalid-sort")


for lib in lib_array:
    movies = plex.library.section(lib)
    items = movies.collections()
    item_total = len(items)
    print(f"{item_total} collection(s) retrieved...")
    item_count = 1
    with alive_bar(item_total, dual_line=True, title="Collection delete - Plex") as bar:
        for item in items:
            title = item.title

            if title in keeper_array:
                bar.text = f"-> keeping: {title}"
            else:
                bar.text = f"-> deleting: {title}"
                item.delete()

            bar()

            # Wait between items in case hammering the Plex server turns out badly.
            time.sleep(DELAY)
