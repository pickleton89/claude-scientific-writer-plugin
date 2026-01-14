# Image Generation Model Reference

> OpenRouter model capabilities and selection guide.
> For current pricing and availability, see: https://openrouter.ai/models

## Recommended Model

**Use `google/gemini-3-pro-image-preview` for all image generation tasks.**

This is the default and recommended model because it:
- Supports generation, editing, AND inpainting (all capabilities)
- Provides excellent quality for scientific visualizations
- Works well with technical and scientific subjects

## Model Capabilities Comparison

| Model | Generation | Editing | Inpainting | Quality | Cost | Status |
|-------|------------|---------|------------|---------|------|--------|
| `google/gemini-3-pro-image-preview` | Yes | Yes | Yes | Excellent | $$ | **Recommended** |
| `black-forest-labs/flux.2-pro` | Yes | Yes | No | Excellent | $$ | ⚠️ Deprecated |
| `black-forest-labs/flux.2-flex` | Yes | No | No | Good | $ | ⚠️ Deprecated |

## Model Details

### Google Gemini 3 Pro Image Preview (Recommended)
- **Model ID:** `google/gemini-3-pro-image-preview`
- **Status:** Active, Recommended
- **Best for:** All use cases - generation, editing, inpainting, scientific visualizations
- **Strengths:** Excellent prompt adherence, good at scientific/technical subjects, full feature support
- **Limitations:** Preview model, may have rate limits

### FLUX.2 Pro (Deprecated)
- **Model ID:** `black-forest-labs/flux.2-pro`
- **Status:** ⚠️ **DEPRECATED** - Use Gemini 3 Pro instead
- **Note:** This model will show deprecation warnings when used. It remains functional but is not recommended for new projects.

### FLUX.2 Flex (Deprecated)
- **Model ID:** `black-forest-labs/flux.2-flex`
- **Status:** ⚠️ **DEPRECATED** - Use Gemini 3 Pro instead
- **Note:** This model will show deprecation warnings when used. It remains functional but is not recommended for new projects.

## Usage Examples

> **Note:** In examples below, run from the `scripts/` directory or adjust the path accordingly.

### Basic Generation (Recommended)
```bash
python generate_image.py "Your prompt here"
```

### With Custom Output Path
```bash
python generate_image.py "Your prompt" --output my_image.png
```

### Image Editing
```bash
python generate_image.py "Make the sky purple" --input photo.jpg --output edited.png
```

## Decision Flow

```
What do you need?
│
├─ Generate new image
│  └─ Use: google/gemini-3-pro-image-preview (default)
│
├─ Edit existing image
│  └─ Use: google/gemini-3-pro-image-preview (default)
│
└─ Inpainting (fill in parts of image)
   └─ Use: google/gemini-3-pro-image-preview (only option)

Note: FLUX.2 models are deprecated. The decision is simple now:
      Always use the default Gemini 3 Pro model.
```

## API Configuration

### Environment Setup
```bash
# Create .env file in project root
echo "OPENROUTER_API_KEY=your-key-here" > .env

# Or export directly
export OPENROUTER_API_KEY=your-key-here
```

### Get API Key
1. Visit https://openrouter.ai/keys
2. Create a new API key
3. Add to `.env` file or environment variable

## Rate Limits and Costs

Check current pricing at: https://openrouter.ai/models

General guidance:
- Gemini 3 Pro: Excellent quality, moderate cost, all features supported
- FLUX models: Deprecated, will show warnings if used

## Migration Guide

If you were using FLUX.2 models, simply remove the `--model` flag to use the default Gemini 3 Pro:

```bash
# Before (deprecated)
python generate_image.py "prompt" --model "black-forest-labs/flux.2-pro"

# After (recommended)
python generate_image.py "prompt"
```

The default model handles all use cases that FLUX.2 supported, plus inpainting.
