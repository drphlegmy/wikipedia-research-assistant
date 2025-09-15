from flask import Flask, request, render_template
from scraper import (
    get_soup_for_topic,
    find_internal_links,
    get_first_paragraph,
    get_categories,
)
from summarizer import clean_text
from filter import filter_by_keyword

# Create the Flask application
app = Flask(__name__)

# Define the main route, accepting both GET (to show the form) and POST (to process it)
@app.route("/", methods=["GET", "POST"])
def index():
    # Check if the user submitted the form
    if request.method == "POST":
        # --- 1) Read form inputs ---
        raw_topic = request.form["topic"]                # The topic string the user entered
        mode = request.form.get("mode", "links")         # Output mode: 'links', 'summaries', or 'filtered'
        limit = int(request.form.get("limit", 5))        # How many related pages to fetch
        keywords = request.form.get("keywords", "").split()  # Split space-separated keywords for filtering

        # --- 2) Fetch the main Wikipedia article (with fuzzy matching) ---
        try:
            # get_soup_for_topic handles exact-match and API fallback
            main_soup, actual_topic = get_soup_for_topic(raw_topic)
        except Exception as e:
            # If both direct and search lookups fail, re-render the form with an error message
            return render_template("index.html", error=str(e))

        # --- 3) Build a dictionary for the main article’s data ---
        main_article = {
            "title": actual_topic.replace("_", " "),  # Convert underscores back to spaces for display
            "url": f"https://en.wikipedia.org/wiki/{actual_topic}",
            "excerpt": "",                            # Will fill in below if needed
            "categories": []                          # Will fill in below if needed
        }
        # Only grab excerpt & categories when in 'summaries' or 'filtered' mode
        if mode in ("summaries", "filtered"):
            raw_para = get_first_paragraph(main_soup)   # Extract the first substantial paragraph
            main_article["excerpt"] = clean_text(raw_para)  # Clean and normalize whitespace/punctuation
            main_article["categories"] = get_categories(main_soup)

        # --- 4) Gather related article links up to the specified limit ---
        all_links = find_internal_links(main_soup)[:limit]  # List of URLs
        related = []
        for url in all_links:
            # Extract just the topic portion from the URL for a second lookup
            subtopic = url.rsplit("/wiki/", 1)[-1]
            try:
                # Re-fetch each related page (also with fuzzy matching)
                page_soup, _ = get_soup_for_topic(subtopic)
            except Exception:
                # Skip any link that fails to load or parse
                continue

            # Build the data object for this related page
            item = {
                "title": subtopic.replace("_", " "),
                "url": url,
                "excerpt": "",
                "categories": []
            }
            # Populate excerpt & categories if needed
            if mode in ("summaries", "filtered"):
                raw_para = get_first_paragraph(page_soup)
                item["excerpt"] = clean_text(raw_para)
                item["categories"] = get_categories(page_soup)

            related.append(item)

        # --- 5) Apply keyword filtering on the related list if requested ---
        if mode == "filtered" and keywords:
            related = filter_by_keyword(related, keywords)

        # --- 6) Render the results page, passing all data to the template ---
        return render_template(
            "results.html",
            original=raw_topic.replace("_", " "),  # The user’s raw input
            main=main_article,                     # The main article data
            related=related,                       # The list of related articles
            mode=mode,
            keywords=keywords,
            limit=limit
        )

    # If GET request, just show the empty search form
    return render_template("index.html")


# Only run the server if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)
