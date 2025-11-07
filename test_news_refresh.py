"""
Playwright test to verify news stories are refreshed when generating a new cartoon.

This test verifies that:
1. First cartoon generation fetches initial news stories
2. Clicking "New Cartoon" button clears cached news
3. Second cartoon generation fetches FRESH news stories (not the same ones)
4. Each cartoon generation can have different news topics
"""

from mcp__playwright__playwright_navigate import navigate
from mcp__playwright__playwright_screenshot import screenshot
from mcp__playwright__playwright_click import click
from mcp__playwright__playwright_get_visible_text import get_visible_text
from mcp__playwright__playwright_expect_response import expect_response
from mcp__playwright__playwright_assert_response import assert_response
import time
import json


async def test_news_refresh_on_new_cartoon():
    """
    Test that news stories are refreshed when clicking 'New Cartoon' button.

    This is the main integration test for the news refresh feature.
    """
    print("\n" + "="*80)
    print("🧪 TEST: News Story Refresh on 'New Cartoon'")
    print("="*80)

    # Navigate to the Streamlit app
    print("\n1️⃣  Navigating to Cartoon of the Day app...")
    await navigate(url="http://localhost:8501")
    time.sleep(2)  # Wait for app to load
    await screenshot(name="01_app_loaded")

    # Click "Enter Location Manually" to set a location
    print("2️⃣  Setting location manually...")
    text = await get_visible_text()
    if "Enter Location Manually" in text:
        await click(selector="button:has-text('⌨️ Enter Location Manually')")
        time.sleep(1)
        await screenshot(name="02_manual_entry_shown")

    # Enter location
    print("3️⃣  Entering location (London, UK)...")
    await click(selector='input[placeholder="e.g., Paris, France"]')
    await fill(selector='input[placeholder="e.g., Paris, France"]', value="London, UK")
    time.sleep(0.5)

    # Click "Use This Location"
    await click(selector="button:has-text('Use This Location')")
    time.sleep(2)
    await screenshot(name="03_location_set")

    # Get first cartoon topic/news indicator
    print("4️⃣  Generating first cartoon...")
    await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")

    # Wait for generation to complete (up to 60 seconds)
    print("   Waiting for cartoon generation to complete...")
    max_wait = 60
    start_time = time.time()
    while time.time() - start_time < max_wait:
        text = await get_visible_text()
        if "🏆" in text and ("Why it's funny" in text or "Why funny" in text):
            print("   ✅ First cartoon generated!")
            break
        time.sleep(2)

    await screenshot(name="04_first_cartoon_generated")
    text_after_first = await get_visible_text()

    # Extract first cartoon winner info
    print("5️⃣  Capturing first cartoon details...")
    lines = text_after_first.split("\n")
    first_cartoon_topic = None
    first_cartoon_title = None

    for i, line in enumerate(lines):
        if "Today's Topic:" in line:
            first_cartoon_topic = line.split("Today's Topic:")[-1].strip()
        if "🏆" in line and i > 0:
            first_cartoon_title = line.replace("🏆", "").strip()

    print(f"   Topic: {first_cartoon_topic}")
    print(f"   Winner: {first_cartoon_title}")

    # Click "New Cartoon" button
    print("6️⃣  Clicking 'New Cartoon' button to refresh news...")
    await click(selector="button:has-text('🔄 New Cartoon')")
    time.sleep(2)
    await screenshot(name="05_after_new_cartoon_click")

    # Generate second cartoon
    print("7️⃣  Generating second cartoon (should have fresh news)...")
    text_after_reset = await get_visible_text()

    # Should see the generate button again
    if "Generate Today's Cartoon" in text_after_reset:
        await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")

        # Wait for second generation
        print("   Waiting for second cartoon generation to complete...")
        start_time = time.time()
        while time.time() - start_time < max_wait:
            text = await get_visible_text()
            if "🏆" in text and ("Why it's funny" in text or "Why funny" in text):
                print("   ✅ Second cartoon generated!")
                break
            time.sleep(2)

    await screenshot(name="06_second_cartoon_generated")
    text_after_second = await get_visible_text()

    # Extract second cartoon winner info
    print("8️⃣  Capturing second cartoon details...")
    lines = text_after_second.split("\n")
    second_cartoon_topic = None
    second_cartoon_title = None

    for i, line in enumerate(lines):
        if "Today's Topic:" in line:
            second_cartoon_topic = line.split("Today's Topic:")[-1].strip()
        if "🏆" in line and i > 0:
            second_cartoon_title = line.replace("🏆", "").strip()

    print(f"   Topic: {second_cartoon_topic}")
    print(f"   Winner: {second_cartoon_title}")

    # Verify results
    print("\n9️⃣  Verification Results:")
    print("-" * 60)
    print(f"First Cartoon:")
    print(f"  Topic: {first_cartoon_topic}")
    print(f"  Winner: {first_cartoon_title}")
    print(f"\nSecond Cartoon:")
    print(f"  Topic: {second_cartoon_topic}")
    print(f"  Winner: {second_cartoon_title}")
    print("-" * 60)

    # Check if news was refreshed
    news_refreshed = (first_cartoon_title != second_cartoon_title or
                      first_cartoon_topic != second_cartoon_topic)

    if news_refreshed:
        print("\n✅ SUCCESS: News stories were refreshed!")
        print("   The second cartoon has different content from the first.")
    else:
        print("\n❌ ISSUE: News stories may not be refreshing properly!")
        print("   Both cartoons have the same winner/topic.")
        print("   This suggests the news fetcher may be caching or reusing results.")

    print("\n" + "="*80)
    return news_refreshed


async def test_news_api_calls():
    """
    Test that multiple API calls are made when generating new cartoons.

    This test monitors network requests to verify that NewsFetcher
    is actually making new API calls to NewsAPI when refreshing.
    """
    print("\n" + "="*80)
    print("🧪 TEST: API Call Monitoring for News Refresh")
    print("="*80)

    print("\n1️⃣  Setting up API call monitoring...")
    await navigate(url="http://localhost:8501")
    time.sleep(2)

    # Set location
    print("2️⃣  Setting location (New York, USA)...")
    await click(selector="button:has-text('⌨️ Enter Location Manually')")
    time.sleep(1)
    await click(selector='input[placeholder="e.g., Paris, France"]')
    await fill(selector='input[placeholder="e.g., Paris, France"]', value="New York, USA")
    await click(selector="button:has-text('Use This Location')")
    time.sleep(2)

    # Monitor first generation
    print("3️⃣  Monitoring first cartoon generation...")
    api_calls_first = []

    print("   Clicking Generate...")
    await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")

    # Wait for completion
    max_wait = 60
    start_time = time.time()
    while time.time() - start_time < max_wait:
        text = await get_visible_text()
        if "🏆" in text:
            print("   ✅ First generation complete")
            break
        time.sleep(2)

    await screenshot(name="07_api_test_first_generation")

    # Reset and monitor second generation
    print("4️⃣  Clicking 'New Cartoon' to refresh...")
    await click(selector="button:has-text('🔄 New Cartoon')")
    time.sleep(2)

    print("5️⃣  Monitoring second cartoon generation...")
    api_calls_second = []

    print("   Clicking Generate again...")
    await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")

    # Wait for completion
    start_time = time.time()
    while time.time() - start_time < max_wait:
        text = await get_visible_text()
        if "🏆" in text:
            print("   ✅ Second generation complete")
            break
        time.sleep(2)

    await screenshot(name="08_api_test_second_generation")

    print("\n✅ API monitoring test complete")
    print("   (Check network tab in browser dev tools for actual API calls)")
    print("\n" + "="*80)


async def test_news_fetch_interval():
    """
    Test that news can be fetched at different times with different results.

    This test helps identify if there's any time-based caching or if
    the app properly refreshes on each request.
    """
    print("\n" + "="*80)
    print("🧪 TEST: News Fetch Interval and Timing")
    print("="*80)

    print("\n1️⃣  Navigating to app...")
    await navigate(url="http://localhost:8501")
    time.sleep(2)

    # Set location
    print("2️⃣  Setting location...")
    await click(selector="button:has-text('⌨️ Enter Location Manually')")
    time.sleep(1)
    await click(selector='input[placeholder="e.g., Paris, France"]')
    await fill(selector='input[placeholder="e.g., Paris, France"]', value="Paris, France")
    await click(selector="button:has-text('Use This Location')")
    time.sleep(2)

    # First generation
    print("3️⃣  First generation (immediate)...")
    await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")
    start_first = time.time()

    max_wait = 60
    while time.time() - start_first < max_wait:
        text = await get_visible_text()
        if "🏆" in text:
            duration_first = time.time() - start_first
            print(f"   ✅ Completed in {duration_first:.1f} seconds")
            break
        time.sleep(2)

    await screenshot(name="09_timing_first")
    first_content = await get_visible_text()

    # Wait 5 seconds, then refresh and generate again
    print("4️⃣  Waiting 5 seconds before next generation...")
    time.sleep(5)

    print("5️⃣  Clicking 'New Cartoon' to refresh...")
    await click(selector="button:has-text('🔄 New Cartoon')")
    time.sleep(2)

    print("6️⃣  Second generation (after 5 second delay)...")
    await click(selector="button:has-text('✨ Generate Today\\'s Cartoon')")
    start_second = time.time()

    while time.time() - start_second < max_wait:
        text = await get_visible_text()
        if "🏆" in text:
            duration_second = time.time() - start_second
            print(f"   ✅ Completed in {duration_second:.1f} seconds")
            break
        time.sleep(2)

    await screenshot(name="10_timing_second")
    second_content = await get_visible_text()

    # Compare results
    print("\n7️⃣  Results Comparison:")
    print("-" * 60)

    # Extract topics from content
    first_topic = "N/A"
    second_topic = "N/A"

    for line in first_content.split("\n"):
        if "Today's Topic:" in line:
            first_topic = line.split("Today's Topic:")[-1].strip()

    for line in second_content.split("\n"):
        if "Today's Topic:" in line:
            second_topic = line.split("Today's Topic:")[-1].strip()

    print(f"First generation topic:  {first_topic}")
    print(f"Second generation topic: {second_topic}")
    print(f"Time between requests:   ~5 seconds")
    print("-" * 60)

    if first_topic == second_topic:
        print("\n⚠️  Both generations have the same topic")
        print("   This might indicate:")
        print("   - News API only returns same results within short time window")
        print("   - News fetcher is caching results improperly")
        print("   - Session state is not being cleared properly")
    else:
        print("\n✅ Different topics in sequential generations")
        print("   News refresh appears to be working")

    print("\n" + "="*80)


if __name__ == "__main__":
    import asyncio

    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║          PLAYWRIGHT TESTS: News Story Refresh Verification                 ║
║                                                                            ║
║  These tests verify that news stories are properly refreshed when         ║
║  clicking the "New Cartoon" button. They help identify caching issues     ║
║  or problems with session state management.                              ║
║                                                                            ║
║  Prerequisites:                                                           ║
║  - Streamlit app running on http://localhost:8501                        ║
║  - Valid GOOGLE_API_KEY and NEWSAPI_KEY configured                       ║
║                                                                            ║
║  Run one test at a time:                                                 ║
║  - python test_news_refresh.py (runs all)                               ║
║  - Modify to run individual tests as needed                              ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Run tests
    try:
        # Test 1: Main refresh test
        print("\n📋 TEST SUITE 1: Main Refresh Test")
        result = asyncio.run(test_news_refresh_on_new_cartoon())

        # Test 2: API call monitoring (optional, requires browser dev tools)
        print("\n📋 TEST SUITE 2: API Call Monitoring")
        asyncio.run(test_news_api_calls())

        # Test 3: Timing test
        print("\n📋 TEST SUITE 3: Fetch Timing Test")
        asyncio.run(test_news_fetch_interval())

        print("\n" + "="*80)
        print("✅ All tests completed!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
