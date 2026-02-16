# Nano Banana Tool - Usage Examples

## Quick Test (Standalone)

```bash
# Use the standalone client (no Amplifier needed)
cd /path/to/mock-generator
python nano_banana.py analyze mockups/design.png "What UI components are visible?"
python nano_banana.py compare mockups/original.png output/current.png "Match percentage?"
```

## In Amplifier Session

### 1. Configure in Bundle

```yaml
# In your bundle.md or .amplifier/settings.yaml
tools:
  - module: tool-nano-banana
```

### 2. Use in Conversation

**Analyze a mockup:**
```
Use nano-banana to analyze mockups/blog-design.png:
"Identify all UI components with semantic names. 
Describe the typography system (fonts, weights).
List the color palette."
```

**Compare mockup with implementation:**
```
Use nano-banana to compare:
  image1: mockups/original.png (label: "Target Design")
  image2: output/screenshot.png (label: "Current Implementation")
  
Prompt: "What is the visual match percentage? 
List the top 3 differences with exact CSS fixes."
```

## Common Prompts

### Component Analysis
```
"List all UI components visible in this mockup with semantic names.
Example: ArticleCard, not just Card."
```

### Typography Analysis
```
"Analyze the typography:
1. How many font families are used?
2. Which text elements use which font?
3. What font weights are needed?
4. Describe font characteristics (serif style, contrast, proportions)"
```

### Font Comparison (for systematic search)
```
"IMAGE 1: Original mockup showing 'Title Text'
IMAGE 2: Comparison grid with 20 font options

Rank the top 2 fonts that match the original most closely."
```

### Detail Validation
```
"IMAGE 1: Original mockup
IMAGE 2: Current implementation

Check these specific details:
[ ] Hero card width vs list card width
[ ] Tab underline position
[ ] Font weights

For each, state: MATCH or DIFFERENT with exact fix."
```

### Iteration Validation
```
"IMAGE 1: Original mockup
IMAGE 2: Current implementation

Overall match %?
What's the #1 visual difference?
Provide exact CSS fix for the biggest issue."
```

## Real Session Example

```
user: I have a mockup, want to implement it

assistant: Let me analyze the mockup first.

  Use nano-banana to analyze mockups/design.png:
  "Comprehensive analysis:
  1. List all UI components with semantic names
  2. Describe typography system (fonts, weights, hierarchy)
  3. Identify color palette
  4. Note spacing patterns (padding, margins, gaps)"

[Tool executes]

assistant: The mockup uses:
  - 2 font system (serif titles + sans body)
  - 5 main components: Header, HeroCard, ArticleList, BottomNav
  - Color palette: #F3EFE7 (cream), #C66E5B (terracotta), #2A2A2A (text)
  
  Let me find matching Google Fonts...

[After implementation]

  Use nano-banana to compare mockups/design.png with output/demo-screenshot.png:
  "Visual match %? Top 3 issues with exact fixes."

[Tool executes]

assistant: 85% match. Top issues:
  1. Hero card narrower than expected (add margin: 0 16px)
  2. Tab underline too short (extend to button width)
  3. Font weight too heavy (use 500 instead of 600)
  
  Shall I apply these fixes?
```

## Tips

**For better results:**
- Be specific in prompts (not "what's different" but "check these 5 specific things")
- Use labels to clarify which image is which
- Ask for exact measurements/fixes, not general observations
- One question at a time for focused analysis

**Integration with systematic searches:**
- Use `compare` operation for batch font ranking
- Use `analyze` for component identification
- Use `compare` with detail checklists for refinement

## API Key

Set environment variable:
```bash
export GOOGLE_API_KEY="your-key-here"
```

Get key from: https://aistudio.google.com/apikey
