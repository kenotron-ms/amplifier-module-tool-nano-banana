"""Tests for NanoBananaTool."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from amplifier_module_tool_nano_banana import NanoBananaTool


def _create_mock_coordinator() -> Any:
    """Create a mock coordinator for testing."""
    coordinator = MagicMock()
    coordinator.hooks = MagicMock()
    coordinator.hooks.emit = AsyncMock()
    return coordinator


def test_tool_properties() -> None:
    """Test tool protocol properties."""
    tool = NanoBananaTool({}, _create_mock_coordinator())

    assert tool.name == "nano-banana"
    assert "VLM" in tool.description
    assert "object" in tool.input_schema.get("type", "")


def test_input_schema() -> None:
    """Test input schema is valid."""
    tool = NanoBananaTool({}, _create_mock_coordinator())
    schema = tool.input_schema

    # Required fields
    assert "operation" in schema["properties"]
    assert "prompt" in schema["properties"]

    # Operations
    operations = schema["properties"]["operation"]["enum"]
    assert "analyze" in operations
    assert "compare" in operations
    assert "generate" in operations


@pytest.mark.asyncio
async def test_analyze_requires_api_key(monkeypatch: Any) -> None:
    """Test that analyze fails gracefully without API key."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    tool = NanoBananaTool({}, _create_mock_coordinator())
    result = await tool.execute(
        {"operation": "analyze", "image_path": "test.png", "prompt": "test"}
    )

    assert not result.success
    assert "GOOGLE_API_KEY" in result.output


@pytest.mark.asyncio
async def test_compare_requires_both_images() -> None:
    """Test that compare validates required images."""
    tool = NanoBananaTool({}, _create_mock_coordinator())

    # Missing image2
    result = await tool.execute(
        {"operation": "compare", "image1_path": "test1.png", "prompt": "test"}
    )

    assert not result.success
    assert "image2_path" in result.output


@pytest.mark.asyncio
async def test_generate_requires_output_path() -> None:
    """Test that generate validates required output_path."""
    tool = NanoBananaTool({}, _create_mock_coordinator())

    # Missing output_path
    result = await tool.execute({"operation": "generate", "prompt": "A beautiful landscape"})

    assert not result.success
    assert "output_path" in result.output


@pytest.mark.asyncio
async def test_generate_validates_number_of_images() -> None:
    """Test that generate validates number_of_images range."""
    tool = NanoBananaTool({}, _create_mock_coordinator())

    # Invalid number (too many)
    result = await tool.execute(
        {
            "operation": "generate",
            "output_path": "output.png",
            "prompt": "test",
            "number_of_images": 5,
        }
    )

    assert not result.success
    assert "number_of_images" in result.output
