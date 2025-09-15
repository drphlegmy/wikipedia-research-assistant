import requests
from bs4 import BeautifulSoup

# Base URL for the MediaWiki API used for searching Wikipedia
API_URL = "https://en.wikipedia.org/w/api.php"


def build_wiki_url(topic: str) -> str:
    """
    Construct a direct Wikipedia article URL from a sanitized topic string.
    
    Args:
        topic: The article title, with spaces replaced by underscores.
    Returns:
        Full URL to the Wikipedia page for that topic.
    """
    return f"https://en.wikipedia.org/wiki/{topic}"


def search_wikipedia(term: str) -> str | None:
    """
    Use the Wikipedia API to find the closest matching article title.
    
    This is used as a fallback when an exact URL lookup fails.
    
    Args:
        term: The search term (spaces OK).
    Returns:
        The title of the top search result (spaces in title), or None if no results.
    """
    # Set up the API query parameters
    params = {
        "action": "query",      # We want to run a query
        "list": "search",       # Return search results
        "srsearch": term,       # The search string
        "format": "json"        # JSON response
    }
    # Send the GET request to the API
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()     # Raise exception for HTTP errors

    data = resp.json()          # Parse JSON response
    hits = data.get("query", {}).get("search", [])
    if not hits:
        # No search results at all
        return None

    # Return the title of the first search result
    return hits[0]["title"]


def get_soup_for_topic(topic: str) -> tuple[BeautifulSoup, str]:
    """
    Fetch and parse the Wikipedia page for a topic, with fallback to search.
    
    1) Try an exact URL lookup (underscores OK).
    2) If that returns 404, call the search API to find the closest match.
    
    Args:
        topic: User-provided topic (spaces or underscores).
    Returns:
        A tuple of:
          - BeautifulSoup object for the fetched page
          - The sanitized title string actually used (underscores, no spaces)
    Raises:
        Exception if both direct lookup and API search fail.
    """
    # 1) Attempt exact match via direct URL
    sanitized = topic.replace(" ", "_")                # Replace spaces → underscores
    url = build_wiki_url(sanitized)
    resp = requests.get(url)
    if resp.status_code == 200:
        # Success: return parsed HTML and the sanitized title
        return BeautifulSoup(resp.text, "html.parser"), sanitized

    # 2) Fallback: use the search API for fuzzy matching
    search_term = topic.replace("_", " ")               # Convert underscores → spaces for API
    match = search_wikipedia(search_term)
    if not match:
        # Neither direct nor search lookup found anything
        raise Exception(f"Womp womp! No page found for '{topic}'.")
    
    # Build URL from the best match returned by the API
    sanitized = match.replace(" ", "_")
    url = build_wiki_url(sanitized)
    resp = requests.get(url)
    if resp.status_code != 200:
        # Found a title but failed to fetch its page
        raise Exception(f"Womp womp! Tried '{match}' but got status {resp.status_code}.")
    
    # Success via search fallback
    return BeautifulSoup(resp.text, "html.parser"), sanitized


def find_internal_links(soup: BeautifulSoup) -> list[str]:
    """
    Extract all in-domain (internal) Wikipedia links from the main content area.
    
    Args:
        soup: BeautifulSoup object of a Wikipedia article page.
    Returns:
        A list of full URLs for internal Wikipedia articles (excluding special pages).
    """
    # Select all <a> tags under the main content that link to /wiki/...
    anchors = soup.select("div.mw-parser-output a[href^='/wiki/']")
    internal = []
    for a in anchors:
        href = a["href"]
        # Skip links with colons (like "File:", "Help:", etc.)
        if ":" not in href:
            internal.append("https://en.wikipedia.org" + href)
    return internal


def get_first_paragraph(soup: BeautifulSoup) -> str:
    """
    Find and return the first substantial paragraph from the article.
    
    Args:
        soup: BeautifulSoup object of a Wikipedia article page.
    Returns:
        Text of the first <p> with more than ~15 words, or empty string if none found.
    """
    # Iterate over each <p> in the main content area
    for p in soup.select("div.mw-parser-output > p"):
        # Use get_text with a space separator to preserve spacing between inline tags
        text = p.get_text(" ", strip=True)
        # Only return paragraphs that are long enough to be meaningful
        if text and len(text.split()) > 15:
            return text
    # No suitable paragraph found
    return ""


def get_categories(soup: BeautifulSoup) -> list[str]:
    """
    Extract the list of category names at the bottom of a Wikipedia page.
    
    Args:
        soup: BeautifulSoup object of a Wikipedia article page.
    Returns:
        List of category strings (empty list if none found).
    """
    # The categories are in the element with id="mw-normal-catlinks"
    container = soup.select_one("#mw-normal-catlinks ul")
    if not container:
        return []

    # Return each <li> text, stripping whitespace
    return [li.get_text(" ", strip=True) for li in container.select("li")]


if __name__ == "__main__":
    # Interactive test when running this file directly
    term = input("Enter topic (spaces or underscores): ")
    try:
        # Fetch the page (with fuzzy-matching fallback)
        soup, actual = get_soup_for_topic(term)
        print(f"Using page: {actual.replace('_', ' ')}\n")
        # Show the first meaningful paragraph
        print("First paragraph:\n", get_first_paragraph(soup))
        # Show the categories
        print("\nCategories:", get_categories(soup))
        # Show the first 5 related article links
        print("\nFirst 5 links:", find_internal_links(soup)[:5])
    except Exception as e:
        # Print any lookup errors
        print(e)
