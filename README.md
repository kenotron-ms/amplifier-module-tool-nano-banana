# Amplifier Tool: Nano Banana Pro

VLM tool for mockup-to-code workflows using Google's Gemini vision model.

## Quick Start (Recommended)

Install as an app bundle — one command, works in every Amplifier session:

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main --app
```

Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Get an API key from: https://aistudio.google.com/apikey

That's it. Every session from now on has access to `nano-banana`.

## Features

- **analyze**: Single image analysis (identify components, fonts, colors, layout)
- **compare**: Two image comparison (mockup vs implementation, match %, visual differences)
- **generate**: Create images from text descriptions using Gemini's image generation

---

## App Bundle — Use It Anywhere

This repo ships as a ready-to-use **Amplifier app bundle**. No installation required — just point Amplifier at the repo and go.

### Quick Start

```bash
export GOOGLE_API_KEY="your-api-key-here"

amplifier run \
  --bundle git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main \
  "Analyze mockups/design.png and tell me all the UI components"
```

### What You Get

- `tool-nano-banana` available in every session (analyze, compare, generate)
- A `nano-banana-expert` agent for full mockup-to-code workflows
- All standard foundation tools (filesystem, bash, web search) included
- `GOOGLE_API_KEY` is the only setup required

### Compose Into Your Own Bundle

Add Nano Banana's VLM capabilities to an existing bundle:

```yaml
# your-bundle.md
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main
```

Or include just the behavior (tool + agent, without overriding your system prompt):

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main#subdirectory=behaviors/nano-banana.yaml
```

### Bundle Structure

```
amplifier-module-tool-nano-banana/
├── bundle.md                          # Root app bundle entry point
├── behaviors/
│   └── nano-banana.yaml               # Reusable behavior (tool + agent + awareness)
├── agents/
│   └── nano-banana-expert.md          # Context-sink expert for VLM workflows
└── context/
    ├── instructions.md                # Lightweight system prompt content
    └── nano-banana-awareness.md       # Delegation awareness pointer
```

---

## Installation (Module Only)

If you want to use `tool-nano-banana` in your own bundle without using this one as an app bundle:

### As an App Bundle (Recommended)

Install once, available in every Amplifier session:

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main --app
```

Or add to your `~/.amplifier/settings.yaml` manually:

```yaml
default_bundle: git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main
```

### Compose into Your Bundle

If you're building your own bundle, include it as a dependency:

```yaml
# In your bundle.md frontmatter
includes:
  - bundle: foundation
  - bundle: git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main
```

### Python Package (Advanced)

For direct Python usage or development:

```bash
# Install from git
uv pip install git+https://github.com/microsoft/amplifier-module-tool-nano-banana

# Or local development
cd amplifier-module-tool-nano-banana
uv pip install -e .
```

Then in your bundle YAML:

```yaml
tools:
  - module: tool-nano-banana
    source: git+https://github.com/microsoft/amplifier-module-tool-nano-banana@main
```

## Configuration

Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Get an API key from: https://aistudio.google.com/apikey

---

## Operations

### analyze

Deep image analysis — identify components, layout, typography, colors.

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

Side-by-side visual diff between two images.

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

### generate

Text-to-image generation via Gemini.

**Input:**
```json
{
  "operation": "generate",
  "output_path": "output/generated-image.png",
  "prompt": "A modern dashboard interface with dark mode, featuring charts and analytics widgets",
  "number_of_images": 1
}
```

**Output:**
```json
{
  "generated_images": ["output/generated-image.png"],
  "count": 1,
  "text": "Generated image showing a modern dashboard..."
}
```

**Parameters:**
- `output_path` (required): Where to save the generated image(s). Supports `.png` and `.jpg/.jpeg`
- `number_of_images` (optional): Number of images to generate (1-4, default: 1)
- `reference_image_path` (optional): Reference image to guide generation style
- When generating multiple images, they're saved with suffixes: `image_1.png`, `image_2.png`, etc.

**Example prompts:**
- "A minimalist login page with soft gradients"
- "Hero section with large typography and abstract background"
- "Mobile app navigation bar with icons for home, search, profile"
- "Data visualization dashboard with multiple chart types"

---

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
    "prompt": "Describe the font characteristics for the title: serif classification, stroke contrast, proportions"
})
```

### Image Generation
```python
# Generate a single mockup concept
result = await session.call_tool("nano-banana", {
    "operation": "generate",
    "output_path": "mockups/hero-concept.png",
    "prompt": "Modern hero section with large heading, subtitle, and CTA button on gradient background"
})

# Generate multiple variations
result = await session.call_tool("nano-banana", {
    "operation": "generate",
    "output_path": "mockups/variations.png",
    "prompt": "Login page with email/password fields and social login buttons",
    "number_of_images": 3
})
# Results: mockups/variations_1.png, mockups/variations_2.png, mockups/variations_3.png
```

---

## Why This Tool?

**Independent:** Not dependent on upstream `amplifier-module-image-generation` changes

**Focused:** Only VLM analysis/comparison/generation (what mockup-to-code needs)

**Simple:** ~150 lines of core logic, easy to understand and modify

**Flexible:** Works standalone, as an app bundle, or composed into other bundles

---

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
