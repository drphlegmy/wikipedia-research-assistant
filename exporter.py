import json
from flask import Flask, render_template_string

def to_text_file(display_items, filename: str):
    """
    Write display_items (a list of dicts) to a plain-text file.
    
    Each item's keys and values are written as "Key: Value" lines,
    with a blank line between items.
    """
    # Open (or create) the target file for writing with UTF-8 encoding
    with open(filename, 'w', encoding='utf-8') as f:
        # Iterate over each dictionary in the list
        for item in display_items:
            # Write each field of the dictionary on its own line
            for key, val in item.items():
                # key.title() capitalizes the first letter of the key
                f.write(f"{key.title()}: {val}\n")
            # After one item, add a blank line for readability
            f.write("\n")

def to_json(display_items, filename: str):
    """
    Write display_items (a list of dicts) to a JSON file.
    
    The JSON is formatted with indentation for easy reading.
    """
    # Open (or create) the target file for writing
    with open(filename, 'w', encoding='utf-8') as f:
        # Dump the list of dictionaries into the file
        # ensure_ascii=False preserves non-ASCII characters
        # indent=2 makes the JSON pretty-printed
        json.dump(display_items, f, ensure_ascii=False, indent=2)

def run_flask_app(data: dict):
    """
    Launch a simple Flask app to display research results in the browser.

    Expects `data` to be a dict containing:
      - 'topic': the main article title
      - 'summary': the main article excerpt
      - 'categories': list of category strings
      - 'results': list of related-article dicts
    """
    # Instantiate the Flask application
    app = Flask(__name__)

    # Inline HTML template string for rendering results
    # Uses Jinja2 templating syntax to insert variables
    template = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Wiki Research Assistant</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        h1 { font-size: 2rem; }
        li { margin-bottom: 1rem; }
      </style>
    </head>
    <body>
      <h1>Topic: {{ topic }}</h1>
      <p><strong>Summary:</strong> {{ summary }}</p>
      <p><strong>Categories:</strong> {{ categories | join(', ') }}</p>
      <h2>Results</h2>
      <ul>
      {% for item in results %}
        <li>
          <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
          {% if item.excerpt %}
            <p>{{ item.excerpt }}</p>
          {% endif %}
          {% if item.categories %}
            <p>Categories: {{ item.categories | join(', ') }}</p>
          {% endif %}
        </li>
      {% endfor %}
      </ul>
    </body>
    </html>
    """

    @app.route('/', methods=['GET'])
    def index():
        """
        Handle GET requests to the root URL.
        Renders the inline HTML template with the provided data.
        """
        return render_template_string(
            template,
            # Pass each expected piece of data into the template context
            topic=data.get('topic', 'Unknown Topic'),
            summary=data.get('summary', ''),
            categories=data.get('categories', []),
            results=data.get('results', [])
        )

    # Run the Flask development server in debug mode
    # debug=True enables live reloading and detailed error pages
    app.run(debug=True)
