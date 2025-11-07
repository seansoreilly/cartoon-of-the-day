#!/usr/bin/env python3
"""Test which Gemini models support image generation."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# List all available models
print("Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    print(f"\nModel: {model.name}")
    print(f"  Display Name: {model.display_name}")
    print(f"  Supported Methods: {model.supported_generation_methods}")

    # Check if it supports image generation
    if 'generateImage' in model.supported_generation_methods:
        print("  ✅ SUPPORTS IMAGE GENERATION!")
    elif 'generateContent' in model.supported_generation_methods:
        # Check if the model name suggests image capabilities
        if 'image' in model.name.lower() or 'imagen' in model.name.lower() or 'vision' in model.name.lower():
            print("  🔍 May support images (has 'image' in name)")

print("\n" + "=" * 60)
print("\nTesting specific models for image generation capability:")

# Test models that might support image generation
test_models = [
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
    'gemini-pro-vision',
    'imagen-3.0-generate-001',
    'imagen-3.0-fast-generate-001'
]

for model_name in test_models:
    print(f"\nTesting {model_name}:")
    try:
        model = genai.GenerativeModel(model_name)

        # Try to generate an image
        prompt = "Generate a simple cartoon image of a happy sun"
        response = model.generate_content(prompt)

        # Check if response contains an image
        has_image = False
        if response and hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                            has_image = True
                            print(f"  ✅ Generated image! MIME: {part.inline_data.mime_type}")
                            break

        if not has_image:
            if hasattr(response, 'text'):
                print(f"  ❌ Text-only response (first 50 chars): {response.text[:50]}")
            else:
                print(f"  ❌ No image in response")

    except Exception as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            print(f"  ❌ Model not found")
        else:
            print(f"  ❌ Error: {error_msg[:100]}")