from typing import List, Dict

def filter_by_keyword(
    items: List[Dict],
    keywords: List[str],
    mode: str = "or"
) -> List[Dict]:
    """
    Filters a list of article dictionaries by matching against provided keywords.
    
    Each item dict should have:
      - 'title': the article title
      - 'excerpt': a snippet of text from the article
      - 'categories': a list of category strings
    
    Args:
        items: List of article dicts to filter.
        keywords: List of keywords to look for.
        mode: 'and' to require all keywords present,
              'or' (default) to require any keyword.
    
    Returns:
        A new list containing only the items that match.
    """
    def matches(item: Dict) -> bool:
        """
        Check if a single item matches the keyword criteria.
        Combines title, excerpt, and categories into a single text blob
        for searching.
        """
        # Build one long lowercase string from the title, excerpt, and categories
        text_blob = " ".join([
            item.get('title', ''),                 # article title
            item.get('excerpt', ''),               # cleaned excerpt
            ' '.join(item.get('categories', []))   # joined categories
        ]).lower()
        
        if mode == 'and':
            # All keywords must appear somewhere in the text_blob
            return all(kw.lower() in text_blob for kw in keywords)
        else:
            # Any one keyword appearing is sufficient
            return any(kw.lower() in text_blob for kw in keywords)

    # Apply the matches() helper to each item, returning only the matching ones
    return [item for item in items if matches(item)]


if __name__ == '__main__':
    # Quick built-in test for manual verification
    sample_items = [
        {
            'title': 'Climate_Change',
            'url': 'https://en.wikipedia.org/wiki/Climate_Change',
            'excerpt': 'Climate change refers to long-term shifts in temperatures and weather patterns...',
            'categories': ['Science', 'Environment']
        },
        {
            'title': 'Political_Science',
            'url': 'https://en.wikipedia.org/wiki/Political_Science',
            'excerpt': 'Political science is the study of politics and government...',
            'categories': ['Politics', 'Academia']
        }
    ]

    # OR mode: should match any item containing "science"
    print('OR filter ("science"):', 
          filter_by_keyword(sample_items, ['science'], mode='or'))

    # AND mode: requires both "science" and "environment"
    print('AND filter ("science", "environment"):', 
          filter_by_keyword(sample_items, ['science', 'environment'], mode='and'))
