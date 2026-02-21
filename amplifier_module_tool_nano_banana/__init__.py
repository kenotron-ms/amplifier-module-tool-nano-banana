"""
Amplifier Tool: Nano Banana Pro

VLM tool for mockup-to-code workflows with image generation capabilities.

Capabilities:
- analyze: Single image analysis (identify components, fonts, colors, etc.)
- compare: Two image comparison (mockup vs implementation, match %, issues)
- generate: Create images from text descriptions using Gemini's image generation

Independent implementation - not dependent on upstream image-generation module.
"""

# Amplifier module metadata
__amplifier_module_type__ = "tool"

import logging
from typing import Any

from amplifier_core import ModuleCoordinator

from .tool import NanoBananaTool

__all__ = ["mount"]
__version__ = "0.1.0"

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None) -> None:
    """Mount nano-banana VLM tool.

    Args:
        coordinator: Module coordinator for registering tools
        config: Optional configuration:
            - api_key: Google API key (or use GOOGLE_API_KEY env var)

    Returns:
        None
    """
    config = config or {}

    # Get session.working_dir capability if not configured
    if "working_dir" not in config:
        working_dir = coordinator.get_capability("session.working_dir")
        if working_dir:
            config["working_dir"] = working_dir
            logger.debug(f"Using session.working_dir: {working_dir}")

    # Create and register tool
    tool = NanoBananaTool(config, coordinator)
    await coordinator.mount("tools", tool, name=tool.name)

    logger.info("Mounted nano-banana VLM tool")
