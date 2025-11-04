"""Enhanced cartoon image generation using OpenRouter for scripts and Google Gemini for images."""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io
import streamlit as st
import os
import requests
import json

from src.utils import get_api_key, sanitize_filename


class ImageGenerator:
    """Generates cartoon images using OpenRouter for scripts and Gemini for images."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image generator.

        Args:
            api_key: Google API key (will use get_api_key() if not provided)
        """
        self.api_key = api_key or get_api_key()
        genai.configure(api_key=self.api_key)

        # Use gemini-2.5-flash-image for image generation
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')

        # Get OpenRouter API key from environment
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

        # OpenRouter configuration - using GPT-5 for comedy writing
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        # GPT-5 models available in 2025:
        # - "openai/gpt-5-chat" - Optimized for conversational/creative tasks (best for comics)
        # - "openai/gpt-5" - Base GPT-5 model
        # - "openai/gpt-5-pro" - Most capable variant
        # - "openai/gpt-5-mini" - Faster, cost-effective variant
        # - "openai/gpt-4o" - Fallback if GPT-5 unavailable
        self.script_model = "openai/gpt-5-chat"  # Using GPT-5-chat for comedy generation

        # Fallback to Gemini if OpenRouter is not configured
        if not self.openrouter_api_key:
            st.warning("OpenRouter API key not found. Using Gemini for script generation.")
            self.text_model = genai.GenerativeModel('gemini-exp-1121')
        else:
            self.text_model = None  # We'll use OpenRouter instead

    def script_comic_strip_openrouter(
        self,
        title: str,
        premise: str,
        location: str
    ) -> Optional[str]:
        """
        Create a detailed comic strip script using OpenRouter's GPT-5 model.
        Generates 5 options and returns the best one.

        Args:
            title: Cartoon title
            premise: Cartoon premise/concept
            location: Location context

        Returns:
            Comic strip script or None if generation fails
        """
        if not self.openrouter_api_key:
            # Fallback to Gemini
            return self.script_comic_strip_gemini(title, premise, location)

        script_prompt = f"""You are a legendary comic strip writer channeling the greatest newspaper cartoonists of all time:
Gary Larson (The Far Side), Bill Watterson (Calvin and Hobbes), Charles Schulz (Peanuts), and Jim Davis (Garfield).

Your mission: Create OBVIOUSLY FUNNY comic strips that make readers laugh out loud. The humor should be:
- IMMEDIATE and CLEAR - No subtle jokes that need explaining
- VISUAL - Use sight gags, physical comedy, and exaggerated reactions
- UNIVERSAL - Draw on timeless comic traditions (slapstick, irony, absurdity, wordplay)
- PUNCHY - Build to a strong, satisfying punchline

CARTOON CONCEPT:
Title: {title}
Premise: {premise}
Location: {location}

TASK: Generate 5 COMPLETELY DIFFERENT comic strip ideas for this concept. Each should be a distinct approach:
1. SLAPSTICK VERSION - Physical comedy, pratfalls, exaggerated reactions (Think Three Stooges meets Calvin and Hobbes)
2. IRONIC TWIST - Unexpected reversal or subversion of expectations (Far Side style absurdity)
3. CHARACTER COMEDY - Personality-driven humor with distinct character voices (Peanuts-style philosophical humor)
4. VISUAL PUN/WORDPLAY - Clever visual or verbal puns that work in comic form (Like classic newspaper strips)
5. ABSURDIST HUMOR - Surreal, unexpected situation comedy (Monty Python meets Garfield)

For EACH of the 5 versions, provide:
- A brief description of the comedic approach
- A 2-3 panel comic strip script with:
  * PANEL descriptions with visual details
  * DIALOGUE that's snappy and funny
  * Clear setup → development → PUNCHLINE structure

Then, EVALUATE all 5 and SELECT THE FUNNIEST ONE. Explain why it's the winner.

Finally, provide the WINNING SCRIPT in detail with:
- Complete panel-by-panel breakdown
- All visual elements that make the joke land
- Dialogue with perfect comic timing
- Visual style notes inspired by classic comic strips

Remember: The goal is OBVIOUS, LAUGH-OUT-LOUD humor that would make Gary Larson proud!"""

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/cartoon-of-the-day",
            "X-Title": "Cartoon of the Day"
        }

        data = {
            "model": self.script_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a master comedy writer who studied under Gary Larson, Bill Watterson, and Charles Schulz. Your specialty is creating OBVIOUSLY FUNNY comic strips that get immediate laughs. You understand visual comedy, comic timing, and the art of the perfect punchline. Every comic you write should make readers laugh out loud, not just smile. Channel the best of The Far Side's absurdity, Calvin and Hobbes' energy, and Peanuts' charm."
                },
                {
                    "role": "user",
                    "content": script_prompt
                }
            ],
            "temperature": 0.9,  # Higher creativity for comedy generation
            "max_tokens": 3000,  # More tokens for 5 options plus evaluation
            "top_p": 0.95
        }

        try:
            response = requests.post(self.openrouter_url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                script = result['choices'][0]['message']['content']
                st.info("✨ Comic script generated using GPT-5 (best of 5 options)")
                return script
            else:
                st.warning("OpenRouter returned empty response, falling back to Gemini")
                return self.script_comic_strip_gemini(title, premise, location)

        except requests.exceptions.RequestException as e:
            st.warning(f"OpenRouter API error: {e}. Falling back to Gemini.")
            return self.script_comic_strip_gemini(title, premise, location)
        except Exception as e:
            st.warning(f"Could not generate comic script with OpenRouter: {e}")
            return self.script_comic_strip_gemini(title, premise, location)

    def script_comic_strip_gemini(
        self,
        title: str,
        premise: str,
        location: str
    ) -> Optional[str]:
        """
        Fallback method to create comic strip script using Gemini.

        Args:
            title: Cartoon title
            premise: Cartoon premise/concept
            location: Location context

        Returns:
            Comic strip script or None if generation fails
        """
        if not self.text_model:
            self.text_model = genai.GenerativeModel('gemini-exp-1121')

        script_prompt = f"""Create a detailed comic strip script for this cartoon concept:

Title: {title}
Concept: {premise}
Setting: {location}

Write a 2-3 panel comic strip script with:
1. Panel descriptions (what visually appears in each panel)
2. Character positions and expressions
3. Dialogue or speech bubbles (if applicable)
4. Visual gags or details that make it funny
5. Color notes and visual emphasis
6. Key visual elements that should be prominent

Format as a structured script that clearly shows the visual progression and humor.
Make it detailed enough for an artist to visualize and draw the complete comic strip."""

        try:
            response = self.text_model.generate_content(script_prompt)
            if response and response.text:
                st.info("📝 Comic script generated using Gemini")
                return response.text
            return None
        except Exception as e:
            st.warning(f"Could not generate comic script with Gemini: {e}")
            return None

    def script_comic_strip(
        self,
        title: str,
        premise: str,
        location: str
    ) -> Optional[str]:
        """
        Main method to create a detailed comic strip script.
        Tries OpenRouter first, falls back to Gemini if needed.

        Args:
            title: Cartoon title
            premise: Cartoon premise/concept
            location: Location context

        Returns:
            Comic strip script or None if generation fails
        """
        return self.script_comic_strip_openrouter(title, premise, location)

    def generate_cartoon_image(
        self,
        title: str,
        premise: str,
        location: str,
        style: str = "newspaper comic strip"
    ) -> Optional[Image.Image]:
        """
        Generate a cartoon image based on the concept.

        Args:
            title: Cartoon title
            premise: Cartoon premise/concept
            location: Location context
            style: Art style for the cartoon

        Returns:
            PIL Image object or None if generation fails
        """
        # First, script the comic strip using OpenRouter/Gemini
        script = self.script_comic_strip(title, premise, location)

        # Build the image prompt (now includes the script)
        prompt = self._build_image_prompt(title, premise, location, style, script)

        try:
            # Generate image using Gemini 2.5 Flash Image
            response = self.model.generate_content(prompt)

            # Extract the generated image
            if response and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'blob'):
                                # Convert blob to PIL Image
                                image_bytes = io.BytesIO(part.blob.data)
                                return Image.open(image_bytes)

            # If no image was generated, return None
            return None

        except Exception as e:
            st.error(f"Could not generate image: {e}")
            return None

    def _build_image_prompt(
        self,
        title: str,
        premise: str,
        location: str,
        style: str,
        script: Optional[str] = None
    ) -> str:
        """
        Build a detailed prompt for Gemini image generation.

        Args:
            title: Cartoon title
            premise: Cartoon premise
            location: Location setting
            style: Art style description
            script: Optional comic strip script

        Returns:
            Formatted prompt string
        """
        # Base prompt
        base_prompt = f"""Create a {style} cartoon based on this concept:

Title: {title}
Premise: {premise}
Setting: {location}"""

        # Add script if available
        if script:
            base_prompt += f"""

COMIC STRIP SCRIPT TO VISUALIZE:
{script}

Please create this as a multi-panel comic strip following the script above."""

        # Add style guidelines
        style_prompt = """

VISUAL STYLE (Mark Knight influence):
- Bold, expressive character designs with exaggerated features
- Strong, confident line work with clear silhouettes
- Vibrant, selective use of color with emphasis on key elements
- Dynamic poses and body language that enhance the humor
- Expressive facial features that clearly convey emotions
- Professional newspaper comic strip layout and composition
- Clean, readable panel divisions
- Clear speech bubbles with legible text placement
- Background details that add context without cluttering

TECHNICAL REQUIREMENTS:
- High contrast for newspaper print reproduction
- Clear visual hierarchy guiding the eye through panels
- Consistent character design across panels
- Professional finish suitable for publication"""

        return base_prompt + style_prompt

    def generate_and_save(
        self,
        cartoon_data: Dict[str, Any],
        use_placeholder: bool = False
    ) -> Optional[Path]:
        """
        Generate and save a cartoon image.

        Args:
            cartoon_data: Dictionary containing cartoon concept data
            use_placeholder: If True, create a placeholder instead

        Returns:
            Path to saved image or None if generation fails
        """
        # Extract winner concept
        winner_title = cartoon_data.get('winner')
        ideas = cartoon_data.get('ideas', [])
        winner_concept = next(
            (idea for idea in ideas if idea['title'] == winner_title),
            None
        )

        if not winner_concept:
            return None

        # Generate or create placeholder
        if use_placeholder:
            image = self._create_placeholder_image(
                winner_concept['title'],
                winner_concept['premise']
            )
        else:
            image = self.generate_cartoon_image(
                winner_concept['title'],
                winner_concept['premise'],
                cartoon_data.get('location', 'Unknown')
            )

        if not image:
            # Fallback to placeholder if generation fails
            image = self._create_placeholder_image(
                winner_concept['title'],
                winner_concept['premise']
            )

        # Save the image
        return self._save_image(image, cartoon_data.get('location', 'unknown'))

    def _create_placeholder_image(
        self,
        title: str,
        premise: str
    ) -> Image.Image:
        """Create a placeholder image for testing."""
        from PIL import Image, ImageDraw, ImageFont

        # Create a blank image
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(image)

        # Draw border
        draw.rectangle(
            [(10, 10), (width-10, height-10)],
            outline='#333333',
            width=3
        )

        # Add text
        try:
            # Try to use a better font if available
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # Draw title
        title_text = f"🎨 {title}"
        draw.text((width//2, 100), title_text, fill='#333333', font=font_title, anchor='mm')

        # Draw premise (wrapped)
        premise_lines = self._wrap_text(premise, 60)
        y_position = 200
        for line in premise_lines[:5]:  # Limit to 5 lines
            draw.text((width//2, y_position), line, fill='#666666', font=font_text, anchor='mm')
            y_position += 30

        # Add placeholder notice
        notice = "[AI-Generated Image Would Appear Here]"
        draw.text((width//2, height-50), notice, fill='#999999', font=font_text, anchor='mm')

        return image

    def _wrap_text(self, text: str, width: int) -> list:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _save_image(self, image: Image.Image, location: str) -> Path:
        """Save image to data/cartoons directory."""
        # Create directory if it doesn't exist
        cartoons_dir = Path("data/cartoons")
        cartoons_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_location = sanitize_filename(location)
        filename = f"{safe_location}_{timestamp}.png"
        filepath = cartoons_dir / filename

        # Save image
        image.save(filepath, "PNG")

        return filepath