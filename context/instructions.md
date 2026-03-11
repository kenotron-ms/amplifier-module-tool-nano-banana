# Nano Banana — Visual AI

You have access to `tool-nano-banana` for visual AI tasks powered by Google Gemini VLM.

## Operations

- **analyze** — Deep image analysis: UI structure, component identification, typography, color palette, code generation from mockups
- **compare** — Side-by-side visual diff: design-vs-implementation fidelity checks, before/after change detection
- **generate** — Text-to-image: create mockups, wireframes, or reference visuals from descriptions (with optional reference image)

## When to Use What

Use `tool-nano-banana` directly for quick, single-operation tasks (e.g., "analyze this screenshot").

For multi-step mockup-to-code workflows, delegate to `nano-banana:nano-banana-expert`.

## Requirements

Set `GOOGLE_API_KEY` in your environment for Gemini API access.
