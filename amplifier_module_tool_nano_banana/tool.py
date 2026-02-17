"""Nano Banana Pro Amplifier Tool implementation."""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any

from amplifier_core import ModuleCoordinator, ToolResult

logger = logging.getLogger(__name__)


class NanoBananaTool:
    """
    Nano Banana Pro VLM tool for Amplifier.

    Provides visual analysis and comparison capabilities using Google's Gemini VLM.

    Operations:
    - analyze: Analyze single image (components, fonts, colors, layout)
    - compare: Compare two images (match %, differences, issues)
    """

    def __init__(self, config: dict[str, Any], coordinator: ModuleCoordinator):
        """Initialize tool with configuration and coordinator.

        Args:
            config: Tool configuration
                - api_key: Google API key (optional, uses GOOGLE_API_KEY env var if not set)
                - working_dir: Working directory for resolving relative paths
            coordinator: Module coordinator for event emission and capabilities
        """
        self.config = config
        self.coordinator = coordinator
        self.api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        self.working_dir = config.get("working_dir")
        self.model = "gemini-3-pro-image-preview"

    @property
    def name(self) -> str:
        return "nano-banana"

    @property
    def description(self) -> str:
        return (
            "Nano Banana Pro VLM for visual analysis and comparison. "
            "Operations: analyze (single image) | compare (two images). "
            "Use for mockup analysis, screenshot comparison, "
            "component identification, typography analysis, and iterative refinement."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze", "compare"],
                    "description": "Operation: analyze (single image) or compare (two images)",
                },
                "prompt": {
                    "type": "string",
                    "description": "Analysis or comparison prompt/question",
                },
                "image_path": {
                    "type": "string",
                    "description": "Image path (required for analyze operation)",
                },
                "image1_path": {
                    "type": "string",
                    "description": (
                        "First image path (required for compare - usually original mockup)"
                    ),
                },
                "image2_path": {
                    "type": "string",
                    "description": (
                        "Second image path (required for compare - "
                        "usually implementation screenshot)"
                    ),
                },
                "image1_label": {
                    "type": "string",
                    "description": "Label for first image (default: 'IMAGE 1')",
                    "default": "IMAGE 1",
                },
                "image2_label": {
                    "type": "string",
                    "description": "Label for second image (default: 'IMAGE 2')",
                    "default": "IMAGE 2",
                },
            },
            "required": ["operation", "prompt"],
        }

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve file path (absolute or relative to working_dir).

        Args:
            path_str: File path string

        Returns:
            Resolved Path object
        """
        path = Path(path_str).expanduser()
        if not path.is_absolute() and self.working_dir:
            path = Path(self.working_dir) / path
        return path

    def _get_mime_type(self, file_path: Path) -> str:
        """Detect MIME type from file extension.

        Args:
            file_path: Path to file

        Returns:
            MIME type string (defaults to image/png if unknown)
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        # Default to PNG if unknown
        return mime_type or "image/png"

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute VLM operation.

        Args:
            input_data: Input parameters matching input_schema

        Returns:
            ToolResult with success status and output/error
        """
        from google import genai  # type: ignore[import-untyped]

        # Check API key
        if not self.api_key:
            error_msg = (
                "GOOGLE_API_KEY environment variable not set. "
                "Get your API key from: https://aistudio.google.com/apikey"
            )
            return ToolResult(success=False, output=error_msg, error={"message": error_msg})

        client = genai.Client(api_key=self.api_key)

        operation = input_data.get("operation")
        prompt = input_data.get("prompt", "")

        try:
            if operation == "analyze":
                image_path_str = input_data.get("image_path")
                if not image_path_str:
                    error_msg = "image_path required for analyze operation"
                    return ToolResult(success=False, output=error_msg, error={"message": error_msg})

                # Resolve path and read image
                image_path = self._resolve_path(image_path_str)

                # Emit event before analysis
                await self.coordinator.hooks.emit(
                    "tool.vlm.analyze",
                    {
                        "image_path": str(image_path),
                        "model": self.model,
                        "prompt_length": len(prompt),
                    },
                )

                with open(image_path, "rb") as f:
                    image_data = f.read()

                mime_type = self._get_mime_type(image_path)

                # VLM analysis
                response = client.models.generate_content(
                    model=self.model,
                    contents=[
                        prompt,
                        {"inline_data": {"mime_type": mime_type, "data": image_data}},
                    ],
                )

                logger.info(f"VLM analysis completed for {image_path}")
                return ToolResult(success=True, output={"analysis": response.text})

            elif operation == "compare":
                image1_path_str = input_data.get("image1_path")
                image2_path_str = input_data.get("image2_path")

                if not image1_path_str or not image2_path_str:
                    error_msg = "image1_path and image2_path required for compare operation"
                    return ToolResult(success=False, output=error_msg, error={"message": error_msg})

                # Resolve paths
                image1_path = self._resolve_path(image1_path_str)
                image2_path = self._resolve_path(image2_path_str)

                # Emit event before comparison
                await self.coordinator.hooks.emit(
                    "tool.vlm.compare",
                    {
                        "image1_path": str(image1_path),
                        "image2_path": str(image2_path),
                        "model": self.model,
                        "prompt_length": len(prompt),
                    },
                )

                # Read images
                with open(image1_path, "rb") as f:
                    image1_data = f.read()

                with open(image2_path, "rb") as f:
                    image2_data = f.read()

                # Get MIME types
                mime_type1 = self._get_mime_type(image1_path)
                mime_type2 = self._get_mime_type(image2_path)

                # Labels
                label1 = input_data.get("image1_label", "IMAGE 1")
                label2 = input_data.get("image2_label", "IMAGE 2")

                # VLM comparison
                response = client.models.generate_content(
                    model=self.model,
                    contents=[
                        prompt,
                        {"inline_data": {"mime_type": mime_type1, "data": image1_data}},
                        f"^ {label1}",
                        {"inline_data": {"mime_type": mime_type2, "data": image2_data}},
                        f"^ {label2}",
                    ],
                )

                logger.info(f"VLM comparison completed for {image1_path} vs {image2_path}")
                return ToolResult(success=True, output={"comparison": response.text})

            else:
                error_msg = f"Unknown operation: {operation}. Use 'analyze' or 'compare'"
                return ToolResult(success=False, output=error_msg, error={"message": error_msg})

        except FileNotFoundError as e:
            error_msg = f"Image file not found: {e}"
            logger.error(error_msg)
            await self.coordinator.hooks.emit(
                "tool.vlm.error", {"error": error_msg, "operation": operation}
            )
            return ToolResult(success=False, output=error_msg, error={"message": error_msg})

        except Exception as e:
            error_msg = f"VLM request failed: {e}"
            logger.error(error_msg)
            await self.coordinator.hooks.emit(
                "tool.vlm.error", {"error": error_msg, "operation": operation}
            )
            return ToolResult(success=False, output=error_msg, error={"message": error_msg})
