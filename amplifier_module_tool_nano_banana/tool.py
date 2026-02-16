"""Nano Banana Pro Amplifier Tool implementation."""

import os
from typing import Any


class NanoBananaTool:
    """
    Nano Banana Pro VLM tool for Amplifier.

    Provides visual analysis and comparison capabilities using Google's Gemini VLM.

    Operations:
    - analyze: Analyze single image (components, fonts, colors, layout)
    - compare: Compare two images (match %, differences, issues)
    """

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

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute VLM operation."""
        from google import genai  # type: ignore[import-untyped]

        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "error": "GOOGLE_API_KEY environment variable not set. "
                "Get your API key from: https://aistudio.google.com/apikey"
            }

        client = genai.Client(api_key=api_key)
        model = "gemini-3-pro-image-preview"

        operation = input_data.get("operation")
        prompt = input_data.get("prompt", "")

        try:
            if operation == "analyze":
                image_path = input_data.get("image_path")
                if not image_path:
                    return {"error": "image_path required for analyze operation"}

                # Read image
                with open(image_path, "rb") as f:
                    image_data = f.read()

                # VLM analysis
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        prompt,
                        {"inline_data": {"mime_type": "image/png", "data": image_data}},
                    ],
                )

                return {"analysis": response.text}

            elif operation == "compare":
                image1_path = input_data.get("image1_path")
                image2_path = input_data.get("image2_path")

                if not image1_path or not image2_path:
                    return {"error": "image1_path and image2_path required for compare operation"}

                # Read images
                with open(image1_path, "rb") as f:
                    image1_data = f.read()

                with open(image2_path, "rb") as f:
                    image2_data = f.read()

                # Labels
                label1 = input_data.get("image1_label", "IMAGE 1")
                label2 = input_data.get("image2_label", "IMAGE 2")

                # VLM comparison
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        prompt,
                        {"inline_data": {"mime_type": "image/png", "data": image1_data}},
                        f"^ {label1}",
                        {"inline_data": {"mime_type": "image/png", "data": image2_data}},
                        f"^ {label2}",
                    ],
                )

                return {"comparison": response.text}

            else:
                return {"error": f"Unknown operation: {operation}. Use 'analyze' or 'compare'"}

        except FileNotFoundError as e:
            return {"error": f"Image file not found: {e}"}

        except Exception as e:
            return {"error": f"VLM request failed: {e}"}
