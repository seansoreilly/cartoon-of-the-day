#!/bin/bash
# Run news story retrieval unit tests with detailed output

echo "================================================================================"
echo "  📝 RUNNING NEWS STORY RETRIEVAL UNIT TESTS"
echo "================================================================================"
echo ""

# Run the specific test class with verbose output
python3 -m pytest tests/test_news_fetcher.py::TestNewsStoriesRetrieval -v --tb=short

echo ""
echo "================================================================================"
echo "  📊 SUMMARY"
echo "================================================================================"
echo ""

# Count passing/failing tests
python3 -m pytest tests/test_news_fetcher.py::TestNewsStoriesRetrieval -q

echo ""
echo "📌 WHAT THESE TESTS DEMONSTRATE:"
echo ""
echo "  1. test_news_stories_retrieved_with_details"
echo "     → Shows 5 news stories are retrieved with complete details"
echo ""
echo "  2. test_news_stories_filtered_by_location"
echo "     → Demonstrates location-based filtering works correctly"
echo ""
echo "  3. test_news_stories_with_sorting_method"
echo "     → Tests popularity-based sorting (trending stories)"
echo ""
echo "  4. test_news_stories_summary_generation"
echo "     → Shows descriptions are truncated for display"
echo ""
echo "  5. test_news_stories_display_format"
echo "     → Demonstrates final data structure for display"
echo ""
echo "================================================================================"
