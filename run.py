"""
Entry point for the HackerNews daily digest scraper.

Usage:
    python run.py            # fetch top 30 stories, save to reports/YYYY-MM-DD.md
    python run.py --limit 10 # fetch top 10 stories
"""

import argparse
import logging
import sys

from scraper.fetcher import fetch_top_stories
from scraper.reporter import generate_report, save_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main(limit: int = 30) -> None:
    logger.info("Fetching top %d HackerNews stories...", limit)
    stories = fetch_top_stories(limit=limit)
    logger.info("Fetched %d stories", len(stories))

    report = generate_report(stories)
    path = save_report(report)
    logger.info("Report saved to %s", path)

    # Print the report to stdout (useful for GitHub Actions logs)
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HackerNews daily digest scraper")
    parser.add_argument("--limit", type=int, default=30, help="Number of stories to fetch")
    args = parser.parse_args()
    main(limit=args.limit)
