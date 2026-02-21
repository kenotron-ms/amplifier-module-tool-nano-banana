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
            "Nano Banana Pro VLM for visual analysis, comparison, and generation. "
            "Operations: analyze (single image) | compare (two images) | "
            "generate (create images). "
            "Use for mockup analysis, screenshot comparison, component identification, "
            "typography analysis, iterative refinement, and image generation."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze", "compare", "generate"],
                    "description": (
                        "Operation: analyze (single image), compare (two images), "
                        "or generate (create image)"
                    ),
                },
                "prompt": {
                    "type": "string",
                    "description": "Analysis, comparison, or generation prompt/question",
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
                "output_path": {
                    "type": "string",
                    "description": (
                        "Output path for generated image (required for generate operation). "
                        "Supports .png and .jpg/.jpeg extensions."
                    ),
                },
                "number_of_images": {
                    "type": "integer",
                    "description": "Number of images to generate (default: 1, max: 4)",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 4,
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

            elif operation == "generate":
                output_path_str = input_data.get("output_path")
                if not output_path_str:
                    error_msg = "output_path required for generate operation"
                    return ToolResult(success=False, output=error_msg, error={"message": error_msg})

                # Resolve output path
                output_path = self._resolve_path(output_path_str)

                # Get number of images to generate
                number_of_images = input_data.get("number_of_images", 1)
                if number_of_images < 1 or number_of_images > 4:
                    error_msg = "number_of_images must be between 1 and 4"
                    return ToolResult(success=False, output=error_msg, error={"message": error_msg})

                # Emit event before generation
                await self.coordinator.hooks.emit(
                    "tool.vlm.generate",
                    {
                        "output_path": str(output_path),
                        "model": self.model,
                        "prompt_length": len(prompt),
                        "number_of_images": number_of_images,
                    },
                )

                # Generate image(s) using Gemini (Nano Banana Pro)
                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt],
                )

                # Process generated images
                generated_paths = []
                image_count = 0

                for part in response.parts:
                    if part.inline_data is not None:
                        # Get the image data
                        image_data = part.inline_data.data

                        # Determine output path for this image
                        if number_of_images == 1:
                            current_output = output_path
                        else:
                            # For multiple images, add suffix: image_1.png, image_2.png, etc.
                            stem = output_path.stem
                            suffix = output_path.suffix
                            current_output = (
                                output_path.parent / f"{stem}_{image_count + 1}{suffix}"
                            )

                        # Ensure parent directory exists
                        current_output.parent.mkdir(parents=True, exist_ok=True)

                        # Save the image
                        with open(current_output, "wb") as f:
                            f.write(image_data)

                        generated_paths.append(str(current_output))
                        image_count += 1

                        # Stop if we've generated enough images
                        if image_count >= number_of_images:
                            break

                if not generated_paths:
                    error_msg = "No images were generated by the model"
                    logger.error(error_msg)
                    return ToolResult(success=False, output=error_msg, error={"message": error_msg})

                logger.info(f"Generated {len(generated_paths)} image(s)")

                result_output = {
                    "generated_images": generated_paths,
                    "count": len(generated_paths),
                }

                # Include any text response from the model
                for part in response.parts:
                    if part.text is not None:
                        result_output["text"] = part.text
                        break

                return ToolResult(success=True, output=result_output)

            else:
                error_msg = (
                    f"Unknown operation: {operation}. Use 'analyze', 'compare', or 'generate'"
                )
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
