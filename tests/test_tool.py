"""Tests for NanoBananaTool."""

import pytest
from amplifier_module_tool_nano_banana import NanoBananaTool


def test_tool_properties():
    """Test tool protocol properties."""
    tool = NanoBananaTool()
    
    assert tool.name == "nano-banana"
    assert "VLM" in tool.description
    assert "schema" in tool.input_schema.get("type", "")


def test_input_schema():
    """Test input schema is valid."""
    tool = NanoBananaTool()
    schema = tool.input_schema
    
    # Required fields
    assert "operation" in schema["properties"]
    assert "prompt" in schema["properties"]
    
    # Operations
    operations = schema["properties"]["operation"]["enum"]
    assert "analyze" in operations
    assert "compare" in operations


@pytest.mark.asyncio
async def test_analyze_requires_api_key(monkeypatch):
    """Test that analyze fails gracefully without API key."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    tool = NanoBananaTool()
    result = await tool.execute({
        "operation": "analyze",
        "image_path": "test.png",
        "prompt": "test"
    })
    
    assert "error" in result
    assert "GOOGLE_API_KEY" in result["error"]


@pytest.mark.asyncio
async def test_compare_requires_both_images():
    """Test that compare validates required images."""
    tool = NanoBananaTool()
    
    # Missing image2
    result = await tool.execute({
        "operation": "compare",
        "image1_path": "test1.png",
        "prompt": "test"
    })
    
    assert "error" in result
    assert "image2_path" in result["error"]
