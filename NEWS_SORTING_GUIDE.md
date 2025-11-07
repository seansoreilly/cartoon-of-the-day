# News Sorting Feature Guide

## Overview
The NewsFetcher now supports configurable sorting methods for fetching news headlines. This allows you to get trending stories, most recent news, or location-relevant articles.

## Available Sorting Methods

| Sort Method | Value | Description | Best For |
|------------|-------|-------------|----------|
| **Relevancy** | `"relevancy"` | Most relevant to location (NewsAPI ranking) | Cartoons (default) |
| **Popularity** | `"popularity"` | Trending/viral stories | Breaking news, viral topics |
| **Published Date** | `"publishedAt"` | Most recent stories | News feeds, chronological order |

## Usage Examples

### Basic Usage (Default - Relevancy)
```python
from src.news_fetcher import NewsFetcher

fetcher = NewsFetcher(api_key="your-key")

# Uses default "relevancy" sorting
news = fetcher.fetch_local_news("Melbourne", "Australia")
```

### Get Most Popular/Trending Stories
```python
# Get trending news for the location
news = fetcher.fetch_local_news(
    "Melbourne", 
    "Australia",
    sort_by="popularity"
)
```

### Get Most Recent Stories
```python
# Get newest stories first
news = fetcher.fetch_local_news(
    "Melbourne",
    "Australia", 
    sort_by="publishedAt"
)
```

### Using fetch_and_summarize
```python
# Get news and summary with custom sorting
result = fetcher.fetch_and_summarize(
    "Melbourne",
    "Australia",
    sort_by="popularity"
)

print(result['sort_by'])  # "popularity"
print(result['summary'])  # News summary
```

### Using Convenience Function
```python
from src.news_fetcher import fetch_news_for_location

# Fetch trending news for a location
news_result = fetch_news_for_location(
    "Melbourne",
    "Australia",
    sort_by="popularity"
)
```

## Returned Data

The `sort_by` method is included in the returned dictionary:

```python
result = fetcher.fetch_and_summarize("Melbourne", "Australia", sort_by="popularity")

print(result)
# {
#     'news_data': {...},
#     'dominant_topic': 'Local News',
#     'summary': '...',
#     'location': 'Melbourne, Australia',
#     'date': '2025-11-07',
#     'sort_by': 'popularity'  # <-- New field
# }
```

## Integration with App

### Streamlit UI Enhancement
You could add a dropdown selector:

```python
sort_method = st.selectbox(
    "How would you like news sorted?",
    ["relevancy", "popularity", "publishedAt"],
    index=0,  # Default to relevancy
    help="relevancy: Most relevant to location, popularity: Trending stories, publishedAt: Most recent"
)

# Fetch news with selected sorting
news = fetch_news_for_location(
    city, 
    country,
    sort_by=sort_method
)
```

## Error Handling

If an invalid `sort_by` value is provided, it automatically falls back to `"relevancy"`:

```python
# Invalid value - silently falls back to "relevancy"
news = fetcher.fetch_local_news(
    "Melbourne",
    "Australia",
    sort_by="invalid_method"  # Falls back to "relevancy"
)
```

## Valid Values

Only these values are accepted:
- `"relevancy"` (default)
- `"popularity"`
- `"publishedAt"`

Any other value triggers a warning and falls back to `"relevancy"`.

## Testing

New test cases verify the sorting functionality:

```bash
# Run all news fetcher tests
pytest tests/test_news_fetcher.py -v

# Run only sorting tests
pytest tests/test_news_fetcher.py::TestConvenienceFunctions::test_fetch_local_news_with_sort_by_popularity -v
```

## Backward Compatibility

✅ **Fully backward compatible**
- Default behavior unchanged (uses `"relevancy"`)
- Existing code continues to work without modification
- Parameter is optional with sensible default
- No breaking changes

## Future Enhancements

Possible improvements:
1. Add UI dropdown in Streamlit for sort method selection
2. Store user's preferred sorting method in session state
3. Compare cartoon quality across different sorting methods
4. Add analytics to track which sorting method produces funnier cartoons

## References

- [NewsAPI Documentation](https://newsapi.org/docs)
- NewsAPI supports: `relevancy`, `popularity`, `publishedAt`
- All sorting methods filter by location (city + country)
- Results limited to past 24 hours by default
