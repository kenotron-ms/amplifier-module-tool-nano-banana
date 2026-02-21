#!/usr/bin/env python3
"""Test script for nano-banana generate operation."""

import asyncio
import os
import sys
from typing import Any


class MockCoordinator:
    """Mock coordinator for testing."""

    class Hooks:
        async def emit(self, event: str, data: dict[str, Any]) -> None:
            print(f"[EVENT] {event}: {data}")

    def __init__(self) -> None:
        self.hooks = self.Hooks()


async def main() -> int:
    """Generate a small banana image."""
    # Import the tool
    from amplifier_module_tool_nano_banana.tool import NanoBananaTool
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable not set")
        print("Get your API key from: https://aistudio.google.com/apikey")
        return 1
    
    # Create mock coordinator
    coordinator = MockCoordinator()
    
    # Initialize tool with working_dir set to current directory
    tool = NanoBananaTool(
        config={"working_dir": os.getcwd()},
        coordinator=coordinator
    )
    
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print()
    print("Generating image of a small banana...")
    print()
    
    # Generate the image
    result = await tool.execute(
        {
            "operation": "generate",
            "output_path": "output/small-banana.png",
            "prompt": (
                "A cute small banana with a happy smiling face, "
                "simple minimalist cartoon style illustration, "
                "cheerful and friendly character, bright yellow color, "
                "on a clean white background"
            ),
            "number_of_images": 1,
        }
    )
    
    if result.success:
        print("✅ SUCCESS!")
        print()
        print(f"Generated images: {result.output.get('generated_images', [])}")
        print(f"Count: {result.output.get('count', 0)}")
        if 'text' in result.output:
            print(f"Model response: {result.output['text']}")
    else:
        print("❌ FAILED")
        print(f"Error: {result.output}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
