"""Cartoon image generation using Google Gemini."""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io
import streamlit as st

from src.utils import get_api_key, sanitize_filename


class ImageGenerator:
    """Generates cartoon images using Gemini."""

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
        # Use gemini-exp-1121 for text-based scripting - most capable model for creative writing
        self.text_model = genai.GenerativeModel('gemini-exp-1121')

    def script_comic_strip(
        self,
        title: str,
        premise: str,
        location: str
    ) -> Optional[str]:
        """
        Create a detailed comic strip script before image generation.

        Args:
            title: Cartoon title
            premise: Cartoon premise/concept
            location: Location context

        Returns:
            Comic strip script or None if generation fails
        """
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
Make it detailed enough for an artist to visualize and draw the complete comic strip.
"""
        try:
            response = self.text_model.generate_content(script_prompt)
            if response and response.text:
                return response.text
            return None
        except Exception as e:
            st.warning(f"Could not generate comic script: {e}")
            return None

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
        # First, script the comic strip
        script = self.script_comic_strip(title, premise, location)

        # Build the image prompt (now includes the script)
        prompt = self._build_image_prompt(title, premise, location, style, script)

        try:
            # Generate image using Gemini 2.5 Flash Image
            response = self.model.generate_content(prompt)

            if response and response.parts:
                for part in response.parts:
                    # Check for inline image data
                    if hasattr(part, 'inline_data') and part.inline_data.data:
                        try:
                            # Convert bytes to PIL Image
                            image = Image.open(io.BytesIO(part.inline_data.data))
                            return image
                        except Exception as img_error:
                            st.error(f"Error processing generated image: {img_error}")
                            return None

            # No image data found in response
            st.warning("No image data in response. Using placeholder.")
            return None

        except Exception as e:
            st.error(f"Error generating image: {e}")
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
        Build an optimized prompt for cartoon image generation.

        Args:
            title: Cartoon title
            premise: Cartoon premise
            location: Location context
            style: Art style
            script: Comic strip script (detailed panel descriptions)

        Returns:
            Optimized image generation prompt
        """
        script_section = ""
        if script:
            script_section = f"""
COMIC STRIP SCRIPT (follow this structure):
{script}

Follow this script precisely to ensure visual coherence and proper humor delivery.
"""

        prompt = f"""Create a {style} cartoon image in the style of Mark Knight (Melbourne cartoonist):

Title: {title}
Concept: {premise}
Setting: {location}
{script_section}

Art style requirements (inspired by Mark Knight):
- Clean, precise line art with sharp details
- Professional newspaper cartoon quality
- Expressive, well-defined characters
- Clever visual humor and wit
- Clear visual storytelling
- Bright, vibrant but balanced colors
- Polished, contemporary cartoon style
- Professional editorial cartoon aesthetics

The cartoon should be:
- Single panel or 2-3 panel strip
- Easily readable and understandable at a glance
- Visually appealing and humorous
- Appropriate for all ages
- Similar quality to professional newspaper editorial cartoons

Focus on visual comedy, clever visual puns, and clear communication of the concept. Emulate the sharp wit and visual sophistication of Mark Knight's editorial cartoons.
"""
        return prompt

    def create_placeholder_image(
        self,
        title: str,
        premise: str,
        width: int = 800,
        height: int = 600
    ) -> Image.Image:
        """
        Create a placeholder image with text when image generation is unavailable.

        Args:
            title: Cartoon title
            premise: Cartoon premise
            width: Image width
            height: Image height

        Returns:
            PIL Image with text
        """
        from PIL import Image, ImageDraw, ImageFont

        # Create a white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        # Draw border
        border_color = '#FF6B6B'
        draw.rectangle([(10, 10), (width-10, height-10)], outline=border_color, width=5)

        # Try to use a font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except IOError:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 50), title, fill='black', font=title_font)

        # Draw premise (wrapped text)
        max_width = width - 100
        words = premise.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=text_font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw wrapped text
        y = 150
        for line in lines[:5]:  # Limit to 5 lines
            bbox = draw.textbbox((0, 0), line, font=text_font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            draw.text((x, y), line, fill='#333333', font=text_font)
            y += 40

        # Draw "Coming Soon" message
        coming_soon = "🎨 Cartoon Image Coming Soon!"
        try:
            cs_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except IOError:
            cs_font = text_font

        bbox = draw.textbbox((0, 0), coming_soon, font=cs_font)
        cs_width = bbox[2] - bbox[0]
        cs_x = (width - cs_width) // 2
        draw.text((cs_x, height - 100), coming_soon, fill=border_color, font=cs_font)

        return image

    def save_image(
        self,
        image: Image.Image,
        cartoon_data: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Save generated image to disk.

        Args:
            image: PIL Image to save
            cartoon_data: Cartoon data dictionary
            output_dir: Output directory (defaults to data/cartoons)

        Returns:
            Path to saved image
        """
        if output_dir is None:
            output_dir = Path("data/cartoons")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        location = cartoon_data.get('location', 'unknown')
        safe_location = sanitize_filename(location)
        filename = f"{safe_location}_{timestamp}.png"

        output_path = output_dir / filename

        # Save image
        image.save(output_path, format='PNG', quality=95)

        return output_path

    def generate_and_save(
        self,
        cartoon_data: Dict[str, Any],
        use_placeholder: bool = False
    ) -> Optional[Path]:
        """
        Generate cartoon image and save it.

        Args:
            cartoon_data: Complete cartoon data dictionary
            use_placeholder: If True, create placeholder instead of generating

        Returns:
            Path to saved image or None if generation fails
        """
        winner = cartoon_data.get('winner')
        ideas = cartoon_data.get('ideas', [])

        # Find winner concept
        winner_concept = None
        for idea in ideas:
            if idea.get('title') == winner:
                winner_concept = idea
                break

        if not winner_concept:
            st.error("Winner concept not found")
            return None

        title = winner_concept['title']
        premise = winner_concept['premise']
        location = cartoon_data.get('location', 'Unknown')

        if use_placeholder:
            # Create placeholder image
            image = self.create_placeholder_image(title, premise)
            return self.save_image(image, cartoon_data)
        else:
            # Generate actual image (when available)
            generated_image = self.generate_cartoon_image(
                title,
                premise,
                location
            )

            if generated_image:
                # Convert to PIL Image if needed
                if not isinstance(generated_image, Image.Image):
                    # Handle different return types
                    try:
                        image = Image.open(io.BytesIO(generated_image))
                    except:
                        st.warning("Could not process generated image, using placeholder")
                        image = self.create_placeholder_image(title, premise)
                else:
                    image = generated_image

                return self.save_image(image, cartoon_data)
            else:
                # Fallback to placeholder
                image = self.create_placeholder_image(title, premise)
                return self.save_image(image, cartoon_data)


def generate_cartoon_image_from_data(
    cartoon_data: Dict[str, Any],
    api_key: Optional[str] = None,
    use_placeholder: bool = False
) -> Optional[Path]:
    """
    Convenience function to generate and save cartoon image.

    Args:
        cartoon_data: Complete cartoon data dictionary
        api_key: Google API key (optional)
        use_placeholder: If True, create placeholder instead of generating

    Returns:
        Path to saved image or None if generation fails
    """
    generator = ImageGenerator(api_key=api_key)
    return generator.generate_and_save(cartoon_data, use_placeholder)
