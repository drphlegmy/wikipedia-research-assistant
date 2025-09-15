import re

def clean_text(text: str) -> str:
    """
    Normalize and clean up raw text by collapsing excess whitespace
    and removing unwanted spaces before punctuation.

    Args:
        text: The raw string extracted from HTML or other sources.

    Returns:
        A cleaned string with:
          - All runs of whitespace reduced to single spaces
          - No space left before punctuation marks .,!?;:
    """
    # 1) Collapse any sequence of whitespace (spaces, tabs, newlines) into a single space
    s = re.sub(r"\s+", " ", text).strip()
    # 2) Remove spaces that appear directly before punctuation characters
    s = re.sub(r"\s+([.,!?;:])", r"\1", s)
    return s

def summarize(text: str, max_sentences: int = 2) -> str:
    """
    Generate a brief summary by taking the first few sentences of cleaned text.

    Args:
        text: The raw or cleaned text to summarize.
        max_sentences: The maximum number of sentences to include.

    Returns:
        A string composed of up to `max_sentences` sentences, joined by spaces.
    """
    # First, ensure the text is cleaned of odd spacing and stray whitespace
    cleaned = clean_text(text)
    # Split the cleaned text at sentence boundaries: look for . or ! or ? followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    # Join and return only the first `max_sentences` sentences
    return " ".join(sentences[:max_sentences])

if __name__ == "__main__":
    # Quick interactive demo when running this file directly
    sample = (
        "    This is    a test.  Here’s a second sentence! "
        "<!-- html comments -->And here's a third?  "
    )
    cleaned = clean_text(sample)
    print("CLEAN:", cleaned)               # Show the effect of clean_text
    print("SUMM:", summarize(sample, 2))   # Show a 2-sentence summary of the sample
