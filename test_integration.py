#!/usr/bin/env python3
"""Integration test - verify tool works."""

import asyncio
import os


async def test_tool():
    """Test the tool can be imported and executed."""
    from amplifier_module_tool_nano_banana import NanoBananaTool
    
    tool = NanoBananaTool()
    
    print("Testing NanoBananaTool")
    print(f"  Name: {tool.name}")
    print(f"  Description: {tool.description[:80]}...")
    print()
    
    # Test without API key
    print("Test 1: Missing API key handling")
    old_key = os.environ.get("GOOGLE_API_KEY")
    if old_key:
        del os.environ["GOOGLE_API_KEY"]
    
    result = await tool.execute({
        "operation": "analyze",
        "image_path": "test.png",
        "prompt": "test"
    })
    
    assert "error" in result
    assert "GOOGLE_API_KEY" in result["error"]
    print("  ✓ Handles missing API key correctly")
    
    if old_key:
        os.environ["GOOGLE_API_KEY"] = old_key
    
    # Test missing required params
    print("\nTest 2: Missing required parameters")
    result = await tool.execute({
        "operation": "compare",
        "image1_path": "test.png",
        "prompt": "test"
        # Missing image2_path
    })
    
    assert "error" in result
    print("  ✓ Validates required parameters")
    
    print("\n✅ All integration tests passed!")


if __name__ == "__main__":
    asyncio.run(test_tool())
