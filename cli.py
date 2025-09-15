"""
cli.py

Command-line interface for the Wikipedia Research Assistant.
Allows users to fetch a main article + related pages, optionally summarize
and filter them, and output to console, text file, or JSON.
"""

import argparse

# Core scraping & parsing functions
from scraper import (
    get_soup_for_topic,
    find_internal_links,
    get_first_paragraph,
    get_categories,
)
# Text cleaning
from summarizer import clean_text
# Filtering by keyword
from filter import filter_by_keyword
# Export utilities for text and JSON output
from exporter import to_text_file, to_json

def main():
    # --- 0) Command-line arguments setup ---
    parser = argparse.ArgumentParser(
        description="Wikipedia Research Assistant CLI"
    )
    # Positional topic argument (spaces or underscores work)
    parser.add_argument(
        "topic",
        help="Wikipedia topic (spaces or underscores allowed)"
    )
    # Mode: just links, summaries, or keyword-filtered results
    parser.add_argument(
        "--mode",
        choices=["links", "summaries", "filtered"],
        default="links",
        help="Output mode: URLs only, with excerpts, or filtered by keywords",
    )
    # How many related pages to fetch
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of related pages to fetch",
    )
    # Keywords for filtering when in 'filtered' mode
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=[],
        help="Space-separated keywords for filtered mode",
    )
    # Where to send results: stdout, text file, or JSON file
    parser.add_argument(
        "--output",
        choices=["console", "text", "json"],
        default="console",
        help="Output destination: console, text file, or JSON file",
    )

    # Parse the arguments into an object
    args = parser.parse_args()

    # --- 1) Resolve the main article topic ---
    # Uses fuzzy matching: exact lookup first, then MediaWiki API fallback
    try:
        soup, actual_topic = get_soup_for_topic(args.topic)
    except Exception as e:
        # If lookup fails, print error and exit
        print(f"Error: {e}")
        return

    # --- 2) Collect related page URLs (up to the requested limit) ---
    # find_internal_links returns all /wiki/ links; slicing enforces limit
    links = find_internal_links(soup)[: args.limit]

    # --- 3) Fetch each related page and build a structured result list ---
    results = []
    for url in links:
        # Extract the wiki page title portion from the URL
        subtopic = url.rsplit("/wiki/", 1)[-1]
        try:
            # Attempt to fetch and parse that subpage (also fuzzy)
            page_soup, _ = get_soup_for_topic(subtopic)
        except Exception:
            # Skip any related link that fails to load
            continue

        # Initialize fields for this item
        title = subtopic                  # raw title (underscores included)
        excerpt = ""                      # will be populated if summaries requested

        # If summaries or filtering is desired, grab & clean the first paragraph
        if args.mode in ("summaries", "filtered"):
            raw_para = get_first_paragraph(page_soup)
            excerpt = clean_text(raw_para)

        # Always grab the categories (empty list if none)
        categories = get_categories(page_soup)

        # Append the item dict to our results
        results.append({
            "title": title,
            "url": url,
            "excerpt": excerpt,
            "categories": categories
        })

    # --- 4) Apply keyword filtering if in 'filtered' mode ---
    if args.mode == "filtered" and args.keywords:
        results = filter_by_keyword(results, args.keywords)

    # --- 5) Output results in the requested format ---
    if args.output == "console":
        # Print each item to stdout with basic formatting
        for item in results:
            print(f"Title: {item['title']}")
            print(f"URL: {item['url']}")
            if args.mode in ("summaries", "filtered"):
                print(f"Excerpt: {item['excerpt']}")
            print(f"Categories: {', '.join(item['categories'])}")
            print()  # blank line between items

    elif args.output == "text":
        # Write to a plain-text file named after the actual topic
        filename = f"{actual_topic}.txt"
        to_text_file(results, filename)
        print(f"Results written to {filename}")

    elif args.output == "json":
        # Write to a JSON file named after the actual topic
        filename = f"{actual_topic}.json"
        to_json(results, filename)
        print(f"Results written to {filename}")

# Entry point: run main() when this script is executed directly
if __name__ == "__main__":
    main()
