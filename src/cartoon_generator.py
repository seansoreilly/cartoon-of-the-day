"""Cartoon concept generation using Google Gemini."""

from typing import List, Dict, Any, Optional
import json
import re
import google.generativeai as genai
import streamlit as st

from src.utils import get_api_key, validate_cartoon_data


class CartoonGenerator:
    """Generates cartoon concepts from news topics."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the cartoon generator.

        Args:
            api_key: Google API key (will use get_api_key() if not provided)
        """
        self.api_key = api_key or get_api_key()
        genai.configure(api_key=self.api_key)
        # Use gemini-2.0-flash-exp for best creative concept generation
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_concepts(
        self,
        topic: str,
        location: str,
        news_context: Optional[str] = None,
        headlines: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate 5 cartoon concepts based on a news topic.

        Args:
            topic: The dominant news topic
            location: Location string (e.g., "Melbourne, Australia")
            news_context: Optional additional context from news headlines
            headlines: Optional list of headline dicts with title, summary, url, source

        Returns:
            Dictionary with 5 ranked cartoon concepts
        """
        prompt = self._build_generation_prompt(topic, location, news_context)

        try:
            response = self.model.generate_content(prompt)
            cartoon_data = self._parse_response(response.text, topic, location)

            # Validate the structure
            if not validate_cartoon_data(cartoon_data):
                st.warning("Generated data didn't match expected structure, fixing...")
                cartoon_data = self._fix_cartoon_data(cartoon_data, topic, location)

            # Attach news URLs to concepts if headlines provided
            if headlines:
                cartoon_data = self._attach_news_urls(cartoon_data, headlines)

            return cartoon_data

        except Exception as e:
            st.error(f"Error generating cartoons: {e}")
            return self._create_fallback_response(topic, location, str(e))

    def _build_generation_prompt(
        self,
        topic: str,
        location: str,
        news_context: Optional[str] = None
    ) -> str:
        """Build the prompt for cartoon generation."""
        context_section = ""
        if news_context:
            context_section = f"\n\nNews context:\n{news_context}"

        return f"""
You are a professional comedy writer in {location} creating cartoon concepts.

Topic: {topic}{context_section}

Your task:
1. Create exactly 5 original, funny cartoon concepts about this topic
2. Each concept must be:
   - Clever and witty
   - Specific to {location} or use local context
   - Appropriate for a general audience
   - Original (not recycling old jokes)

3. Rank them from funniest (#1) to least funny (#5)
4. Select the #1 concept as the winner

Return ONLY valid JSON in this exact format:
{{
  "topic": "{topic}",
  "location": "{location}",
  "ideas": [
    {{
      "title": "Cartoon Title 1",
      "premise": "One sentence describing the cartoon concept",
      "why_funny": "Brief explanation (max 15 words)"
    }},
    {{
      "title": "Cartoon Title 2",
      "premise": "One sentence describing the cartoon concept",
      "why_funny": "Brief explanation (max 15 words)"
    }},
    {{
      "title": "Cartoon Title 3",
      "premise": "One sentence describing the cartoon concept",
      "why_funny": "Brief explanation (max 15 words)"
    }},
    {{
      "title": "Cartoon Title 4",
      "premise": "One sentence describing the cartoon concept",
      "why_funny": "Brief explanation (max 15 words)"
    }},
    {{
      "title": "Cartoon Title 5",
      "premise": "One sentence describing the cartoon concept",
      "why_funny": "Brief explanation (max 15 words)"
    }}
  ],
  "ranking": ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"],
  "winner": "Title 1"
}}

IMPORTANT: Return ONLY the JSON, no markdown code blocks, no extra text.
"""

    def _parse_response(
        self,
        response_text: str,
        topic: str,
        location: str
    ) -> Dict[str, Any]:
        """Parse the API response into structured data."""
        # Remove markdown code blocks if present
        text = response_text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                # Ensure required fields exist
                if 'topic' not in data:
                    data['topic'] = topic
                if 'location' not in data:
                    data['location'] = location
                return data
            except json.JSONDecodeError as e:
                st.error(f"JSON parsing error: {e}")

        # If parsing fails, create fallback
        return self._create_fallback_response(topic, location, "Parse error")

    def _fix_cartoon_data(
        self,
        data: Dict[str, Any],
        topic: str,
        location: str
    ) -> Dict[str, Any]:
        """Fix cartoon data structure if it's invalid."""
        fixed_data = {
            'topic': data.get('topic', topic),
            'location': data.get('location', location),
            'ideas': [],
            'ranking': [],
            'winner': ''
        }

        # Ensure we have 5 ideas
        ideas = data.get('ideas', [])
        while len(ideas) < 5:
            ideas.append({
                'title': f"Concept {len(ideas) + 1}",
                'premise': "A funny cartoon concept",
                'why_funny': "It's humorous"
            })

        # Fix each idea structure
        for i, idea in enumerate(ideas[:5]):
            fixed_idea = {
                'title': idea.get('title', f"Concept {i + 1}"),
                'premise': idea.get('premise', 'A funny concept'),
                'why_funny': idea.get('why_funny', "It's funny")[:50]  # Limit length
            }
            fixed_data['ideas'].append(fixed_idea)

        # Create ranking
        ranking = data.get('ranking', [])
        if len(ranking) != 5:
            ranking = [idea['title'] for idea in fixed_data['ideas']]

        fixed_data['ranking'] = ranking
        fixed_data['winner'] = ranking[0] if ranking else fixed_data['ideas'][0]['title']

        return fixed_data

    def _create_fallback_response(
        self,
        topic: str,
        location: str,
        error: str
    ) -> Dict[str, Any]:
        """Create a fallback response when generation fails."""
        return {
            'topic': topic,
            'location': location,
            'ideas': [
                {
                    'title': f"News Update: {topic}",
                    'premise': f"A humorous take on {topic} in {location}",
                    'why_funny': "Satire of current events"
                },
                {
                    'title': "Local Perspective",
                    'premise': f"Locals react to {topic}",
                    'why_funny': "Relatable community humor"
                },
                {
                    'title': "Breaking News",
                    'premise': f"News anchor struggles with {topic}",
                    'why_funny': "Media satire"
                },
                {
                    'title': "The Interview",
                    'premise': f"Interviewing people about {topic}",
                    'why_funny': "Man on the street humor"
                },
                {
                    'title': "The Aftermath",
                    'premise': f"Life after {topic}",
                    'why_funny': "Exaggerated consequences"
                }
            ],
            'ranking': [
                f"News Update: {topic}",
                "Local Perspective",
                "Breaking News",
                "The Interview",
                "The Aftermath"
            ],
            'winner': f"News Update: {topic}",
            'error': error
        }

    def _attach_news_urls(
        self,
        cartoon_data: Dict[str, Any],
        headlines: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Attach news URLs and sources to cartoon concepts.

        Args:
            cartoon_data: Generated cartoon data
            headlines: List of news headlines with url, source, title

        Returns:
            Updated cartoon data with news URLs attached
        """
        # Use the primary headline URL as the main source
        if headlines and len(headlines) > 0:
            primary_headline = headlines[0]
            cartoon_data['news_url'] = primary_headline.get('url', '')
            cartoon_data['news_source'] = primary_headline.get('source', '')
            cartoon_data['news_title'] = primary_headline.get('title', '')

            # Attach URLs to each idea (primary source for all)
            for idea in cartoon_data.get('ideas', []):
                idea['news_url'] = primary_headline.get('url', '')
                idea['news_source'] = primary_headline.get('source', '')

        return cartoon_data

    def get_winner(self, cartoon_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract the winning cartoon concept.

        Args:
            cartoon_data: Cartoon data dictionary

        Returns:
            Dictionary with winner details
        """
        winner_title = cartoon_data.get('winner')
        ideas = cartoon_data.get('ideas', [])

        for idea in ideas:
            if idea.get('title') == winner_title:
                return {
                    'title': idea['title'],
                    'premise': idea['premise'],
                    'why_funny': idea['why_funny'],
                    'topic': cartoon_data.get('topic', ''),
                    'location': cartoon_data.get('location', '')
                }

        # Fallback to first idea
        if ideas:
            return {
                'title': ideas[0]['title'],
                'premise': ideas[0]['premise'],
                'why_funny': ideas[0]['why_funny'],
                'topic': cartoon_data.get('topic', ''),
                'location': cartoon_data.get('location', '')
            }

        return {}

    def rank_concepts(self, cartoon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get concepts in ranked order.

        Args:
            cartoon_data: Cartoon data dictionary

        Returns:
            List of concept dictionaries in rank order
        """
        ranking = cartoon_data.get('ranking', [])
        ideas = cartoon_data.get('ideas', [])

        ranked_concepts = []
        for title in ranking:
            for idea in ideas:
                if idea.get('title') == title:
                    ranked_concepts.append(idea)
                    break

        # Add any ideas that weren't in the ranking
        for idea in ideas:
            if idea not in ranked_concepts:
                ranked_concepts.append(idea)

        return ranked_concepts


def generate_cartoons_from_news(
    news_data: Dict[str, Any],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate cartoons from news data.

    Args:
        news_data: News data from NewsFetcher
        api_key: Google API key (optional)

    Returns:
        Cartoon data dictionary
    """
    generator = CartoonGenerator(api_key=api_key)

    topic = news_data.get('dominant_topic', 'General News')
    location = news_data.get('location', 'Unknown')
    news_summary = news_data.get('summary', '')
    headlines = news_data.get('headlines', [])

    return generator.generate_concepts(topic, location, news_summary, headlines)
