#!/usr/bin/env python3
"""Unit tests for Gemini image generation functionality."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_models():
    """Test that Gemini models are available and configured correctly."""
    print("=" * 60)
    print("TESTING GEMINI MODELS AVAILABILITY")
    print("=" * 60)

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    else:
        print(f"✅ API Key found: {api_key[:10]}...")

    genai.configure(api_key=api_key)

    # Test each model we use
    models_to_test = [
        ('gemini-2.0-flash-exp', 'Cartoon concept generation'),
        ('gemini-2.0-flash', 'Comic script generation'),
        ('gemini-2.5-flash-image', 'Image generation')
    ]

    print("\nTesting model availability:")
    all_models_work = True

    for model_name, purpose in models_to_test:
        print(f"\n{model_name} ({purpose}):")
        try:
            model = genai.GenerativeModel(model_name)
            # Try a simple generation
            response = model.generate_content("Say 'hello' in one word")
            if response and response.text:
                print(f"  ✅ Model works! Response: {response.text.strip()}")
            else:
                print(f"  ⚠️ Model responded but no text returned")
                all_models_work = False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_models_work = False

    return all_models_work


def test_image_generation():
    """Test actual image generation with Gemini."""
    print("\n" + "=" * 60)
    print("TESTING IMAGE GENERATION")
    print("=" * 60)

    api_key = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=api_key)

    # Test with gemini-2.5-flash-image
    print("\nTrying to generate an image with gemini-2.5-flash-image...")

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image')

        prompt = """Create a simple cartoon image of a cat wearing a hat.

        Style: Simple, colorful cartoon
        Background: Plain white
        Subject: A friendly orange cat wearing a blue hat"""

        print(f"Prompt: {prompt[:100]}...")

        response = model.generate_content(prompt)

        if response:
            print(f"Response received: {response}")

            # Check if response contains an image
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'blob'):
                                print("  ✅ Image blob found in response!")
                                # Try to create PIL image
                                try:
                                    image_bytes = io.BytesIO(part.blob.data)
                                    img = Image.open(image_bytes)
                                    print(f"  ✅ Successfully created PIL Image: {img.size}")
                                    # Save test image
                                    img.save("test_gemini_image.png")
                                    print("  ✅ Saved test image as test_gemini_image.png")
                                    return True
                                except Exception as e:
                                    print(f"  ❌ Could not create PIL image: {e}")
                            elif hasattr(part, 'text'):
                                print(f"  📝 Text part found: {part.text[:100]}")
                            else:
                                print(f"  ❓ Unknown part type: {type(part)}")
            else:
                print("  ⚠️ No candidates in response")

            # Check if it's a text-only response
            if hasattr(response, 'text'):
                print(f"  📝 Text response: {response.text[:200]}")
                print("  ⚠️ Model returned text instead of image - model might not support image generation")
        else:
            print("  ❌ No response from model")

    except Exception as e:
        print(f"  ❌ Error generating image: {e}")
        print(f"      Error type: {type(e).__name__}")
        return False

    return False


def test_alternative_image_models():
    """Test alternative Gemini models that might support image generation."""
    print("\n" + "=" * 60)
    print("TESTING ALTERNATIVE IMAGE GENERATION MODELS")
    print("=" * 60)

    api_key = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=api_key)

    # List of potential image generation models to try
    alternative_models = [
        'gemini-2.5-flash-image',
        'gemini-pro-vision',
        'imagen-3',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]

    for model_name in alternative_models:
        print(f"\nTrying {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)

            # Try to generate an image
            prompt = "Generate a simple cartoon of a happy sun"
            response = model.generate_content(prompt)

            if response:
                # Check for image in response
                has_image = False
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'blob'):
                                    has_image = True
                                    print(f"  ✅ {model_name} can generate images!")
                                    break

                if not has_image and hasattr(response, 'text'):
                    print(f"  ⚠️ {model_name} returned text only")

        except Exception as e:
            print(f"  ❌ {model_name} error: {str(e)[:100]}")


def test_openrouter_image_generator():
    """Test the actual ImageGenerator class from our code."""
    print("\n" + "=" * 60)
    print("TESTING IMAGE GENERATOR CLASS")
    print("=" * 60)

    from src.image_generator_openrouter import ImageGenerator

    try:
        generator = ImageGenerator()
        print("✅ ImageGenerator initialized")

        # Test image generation
        print("\nTesting cartoon image generation...")
        image = generator.generate_cartoon_image(
            title="Test Cartoon",
            premise="A test cartoon for debugging",
            location="Test City",
            style="simple cartoon"
        )

        if image:
            print(f"✅ Image generated successfully: {image.size}")
            image.save("test_cartoon_output.png")
            print("✅ Saved as test_cartoon_output.png")
        else:
            print("❌ Image generation returned None - using placeholder")

    except Exception as e:
        print(f"❌ Error in ImageGenerator: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n🔬 GEMINI IMAGE GENERATION TEST SUITE\n")

    # Test 1: Model availability
    models_ok = test_gemini_models()

    # Test 2: Image generation
    image_ok = test_image_generation()

    # Test 3: Alternative models
    test_alternative_image_models()

    # Test 4: Our actual implementation
    test_openrouter_image_generator()

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Models Available: {'✅' if models_ok else '❌'}")
    print(f"Image Generation: {'✅' if image_ok else '❌'}")

    if not image_ok:
        print("\n⚠️ ISSUE DETECTED: Gemini models may not support direct image generation")
        print("📝 RECOMMENDATION: Use a different approach:")
        print("  1. Use DALL-E 3 via OpenAI API for image generation")
        print("  2. Use Stable Diffusion via Replicate or Hugging Face")
        print("  3. Use Imagen via Google Cloud (different from Gemini)")
        print("  4. Check if Gemini requires special configuration for images")


if __name__ == "__main__":
    main()