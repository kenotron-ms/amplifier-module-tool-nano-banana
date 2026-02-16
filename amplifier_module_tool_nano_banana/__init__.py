"""
Amplifier Tool: Nano Banana Pro

VLM tool for mockup-to-code workflows.

Capabilities:
- analyze: Single image analysis (identify components, fonts, colors, etc.)
- compare: Two image comparison (mockup vs implementation, match %, issues)

Independent implementation - not dependent on upstream image-generation module.
"""

from .tool import NanoBananaTool

__all__ = ["NanoBananaTool"]
__version__ = "0.1.0"
