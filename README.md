# Amplifier Tool: Nano Banana Pro

VLM tool for mockup-to-code workflows using Google's Gemini vision model.

## Features

- **analyze**: Single image analysis (identify components, fonts, colors, layout)
- **compare**: Two image comparison (mockup vs implementation, match %, visual differences)

## Installation

```bash
# Install from git
uv pip install git+https://github.com/microsoft/amplifier-module-tool-nano-banana

# Or local development
cd amplifier-module-tool-nano-banana
uv pip install -e .
```

## Configuration

Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Get an API key from: https://aistudio.google.com/apikey

## Usage in Amplifier

### In Bundle Configuration

```yaml
tools:
  - module: tool-nano-banana
    # No additional config needed - uses GOOGLE_API_KEY from environment
```

### In Agent Sessions

**Analyze a mockup:**
```
Use nano-banana to analyze mockups/design.png:
"Identify all UI components, their layout, and spacing patterns"
```

**Compare mockup with implementation:**
```
Use nano-banana to compare mockups/original.png with output/screenshot.png:
"What is the visual match percentage? List the top 3 differences."
```

## Operations

### analyze

Analyze a single image with VLM.

**Input:**
```json
{
  "operation": "analyze",
  "image_path": "mockups/design.png",
  "prompt": "Identify all UI components and describe the layout hierarchy"
}
```

**Output:**
```json
{
  "analysis": "The mockup contains: 1. Header with title and tabs..."
}
```

**Example prompts:**
- "What UI components are visible?"
- "Describe the typography system (fonts, weights, sizes)"
- "What colors are used in this design?"
- "Identify the spacing/padding patterns"
- "What icons are shown in the bottom navigation?"

### compare

Compare two images with VLM.

**Input:**
```json
{
  "operation": "compare",
  "image1_path": "mockups/original.png",
  "image2_path": "output/implementation.png",
  "prompt": "What is the visual match percentage? What are the main differences?",
  "image1_label": "Original Mockup",
  "image2_label": "Current Implementation"
}
```

**Output:**
```json
{
  "comparison": "Visual match: 85%. Main differences: 1. Hero card width..."
}
```

**Example prompts:**
- "What is the overall match percentage?"
- "What's the biggest visual difference?"
- "Does the typography match?"
- "Are the spacing and margins correct?"
- "Provide the top 3 issues to fix next"

## Use Cases

### Mockup Analysis
```python
result = await session.call_tool("nano-banana", {
    "operation": "analyze",
    "image_path": "mockups/app-design.png",
    "prompt": "Generate a comprehensive component breakdown with semantic names"
})
```

### Iterative Refinement
```python
# Screenshot → Compare → Fix loop
result = await session.call_tool("nano-banana", {
    "operation": "compare",
    "image1_path": "mockups/original.png",
    "image2_path": "output/current-state.png",
    "prompt": "Match %? What's the #1 issue to fix next with exact CSS?"
})
```

### Font Identification
```python
result = await session.call_tool("nano-banana", {
    "operation": "analyze",
    "image_path": "mockups/design.png",
    "prompt": "Describe the font characteristics for the title 'Meditations': serif classification, stroke contrast, proportions"
})
```

### Icon Analysis
```python
result = await session.call_tool("nano-banana", {
    "operation": "analyze",
    "image_path": "mockups/design.png",
    "prompt": "Describe what the navigation icons LOOK like visually (shapes, not concepts)"
})
```

## Why This Tool?

**Independent:** Not dependent on upstream `amplifier-module-image-generation` changes

**Focused:** Only VLM analysis/comparison (what mockup-to-code needs)

**Simple:** ~150 lines of code, easy to understand and modify

**Flexible:** Works standalone or in Amplifier bundles/recipes

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run checks
ruff check .
pyright
pytest
```

## License

MIT
