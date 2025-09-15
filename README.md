# Wikipedia Research Assistant

*Written by drphlegmy*

A simple Python tool that lets you explore a Wikipedia topic and its related articles.  
Choose to run it as a command-line interface (CLI) or as a web app (Flask).

---

## Features
- Fetches the main article (with summary & categories)  
- Gathers internal “related” links  
- Optional excerpts for deeper research  
- Keyword filtering of related links  
- Export results to console, text file, or JSON  
- Web front-end with a single “Search” form  

---

## Prerequisites
- Python 3.7 or higher  
- Git (optional, to clone the repo)  
- Internet connection  

---

## Installation

1. Clone the repository (or unzip your folder):
   ```bash
   git clone <your-repo-URL> wiki_research_assistant
   cd wiki_research_assistant
   ```

2. Create a virtual environment:  
   - macOS / Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```bash
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
     - If PowerShell blocks the script, you can instead open CMD:
       ```bash
       .\.venv\Scripts\activate.bat
       ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:  
   `beautifulsoup4`, `requests`, `flask`, `colorama`, `textblob`, `tqdm`, and more.

---

## Project Structure
```
app.py             # Flask web application  
cli.py             # Command-line interface  
scraper.py         # Fetch & parse Wikipedia pages  
summarizer.py      # Clean & summarize text  
filter.py          # Keyword filtering logic  
exporter.py        # Save to text or JSON (used by CLI)  
requirements.txt   # Pinned dependencies  
/templates/        # Jinja2 HTML templates  
  index.html  
  results.html  
/static/           # CSS and other static files  
  style.css  
```

---

## Usage

### A) Command-Line Interface
- Run and pass your topic (spaces or underscores allowed):  
  ```bash
  python cli.py "climate change"
  ```

- Common flags:  
  - `--mode`       links | summaries | filtered  
  - `--limit`      *number of related pages to fetch*  
  - `--keywords`   *space-separated list* (only for filtered)  
  - `--output`     console | text | json  

- Examples:
  ```bash
  python cli.py "climate change"
  python cli.py "dream daddy" --mode summaries --limit 3
  python cli.py "climate change" --mode filtered \
       --keywords environment politics --output text
  ```

- Text/JSON output files are named `<Topic>.txt` or `<Topic>.json` in your project folder.

---

### B) Web App (Flask)
1. Ensure Flask is installed (from step 3 above).  
2. Run the app:
   ```bash
   python app.py
   ```
3. Open your browser to:  
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)  
4. Enter a topic, choose mode/limit/keywords, and click **Search**.  
5. View the main article and related articles on a modern, card-style page.

---

## Error Handling
- If the exact wiki URL 404s, the app auto-searches via the MediaWiki API  
- Unmatched topics show a red error banner on the search page  
- Broken related links are skipped without breaking the page  
- Empty excerpts/categories simply render as blank  

---

✨ Enjoy diving deep into Wikipedia!
