"""
Fetches top stories from the HackerNews public API.

HackerNews Firebase API (no auth, no scraping — fully public JSON):
  Top story IDs: https://hacker-news.firebaseio.com/v2/topstories.json
  Story detail:  https://hacker-news.firebaseio.com/v2/item/{id}.json
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v2"
TOP_STORIES_URL = f"{HN_BASE}/topstories.json"
ITEM_URL = f"{HN_BASE}/item/{{item_id}}.json"

TIMEOUT = 10  # seconds per request
MAX_WORKERS = 10  # parallel fetches


def get_top_story_ids(limit: int = 30) -> list[int]:
    """Return the IDs of the top N HackerNews stories."""
    resp = requests.get(TOP_STORIES_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()[:limit]


def get_story(item_id: int) -> dict | None:
    """Fetch a single story by ID. Returns None on error."""
    try:
        resp = requests.get(ITEM_URL.format(item_id=item_id), timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Only return stories (not comments, jobs, polls)
        if data and data.get("type") == "story" and data.get("title"):
            return data
    except requests.RequestException as e:
        logger.warning("Failed to fetch item %s: %s", item_id, e)
    return None


def fetch_top_stories(limit: int = 30) -> list[dict]:
    """
    Fetch the top N HackerNews stories in parallel.

    Returns a list of story dicts, each containing at minimum:
      id, title, url (may be absent for text posts), score, by, descendants, time
    """
    ids = get_top_story_ids(limit=limit * 2)  # over-fetch to account for non-stories

    stories = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_story, sid): sid for sid in ids}
        for future in as_completed(futures):
            result = future.result()
            if result:
                stories.append(result)
            if len(stories) >= limit:
                break

    # Sort by score descending (parallel fetch returns in completion order)
    stories.sort(key=lambda s: s.get("score", 0), reverse=True)
    return stories[:limit]
