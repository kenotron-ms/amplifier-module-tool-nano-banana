---
bundle:
  name: nano-banana-test
  version: 0.1.0

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-stories@main#subdirectory=behaviors/stories.yaml

tools:
  - module: tool-nano-banana
    source: file:///Users/ken/workspace/amplifier-module-tool-nano-banana
---

# Nano Banana Test Bundle

Test bundle for using the local nano-banana tool.
