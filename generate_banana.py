#!/usr/bin/env python3
"""Standalone script to generate a small banana image."""

import asyncio
import os


async def generate_small_banana() -> None:
    """Generate a small banana image using Google Gemini."""
    from google import genai
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set")
        print("Get your API key from: https://aistudio.google.com/apikey")
        return
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Generate the image
    prompt = (
        "A cute small banana with a happy smiling face, "
        "simple minimalist cartoon style illustration, "
        "cheerful and friendly character, bright yellow color, "
        "on a clean white background"
    )
    
    print("🍌 Generating small banana image...")
    print(f"Prompt: {prompt}")
    print()
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )
        
        # Save generated images
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        image_count = 0
        for part in response.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                output_path = f"{output_dir}/small-banana.png"
                
                with open(output_path, "wb") as f:
                    f.write(image_data)
                
                image_count += 1
                print(f"✅ Generated: {output_path}")
        
        if image_count == 0:
            print("❌ No images were generated")
        else:
            print(f"\n🎉 Successfully generated {image_count} image(s)!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(generate_small_banana())
