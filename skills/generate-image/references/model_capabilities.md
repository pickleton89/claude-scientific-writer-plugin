# Image Generation Model Reference

> OpenRouter model capabilities and selection guide.
> For current pricing and availability, see: https://openrouter.ai/models

## Model Selection Matrix

| Use Case | Recommended Model | Rationale |
|----------|------------------|-----------|
| High-quality generation | `google/gemini-3-pro-image-preview` | Best overall quality |
| Fast generation | `black-forest-labs/flux.2-pro` | Speed + quality balance |
| Image editing | `google/gemini-3-pro-image-preview` | Best editing capabilities |
| Budget generation | `black-forest-labs/flux.2-flex` | Lower cost option |

## Model Capabilities Comparison

| Model | Generation | Editing | Quality | Cost |
|-------|------------|---------|---------|------|
| `google/gemini-3-pro-image-preview` | Yes | Yes | Excellent | $$ |
| `black-forest-labs/flux.2-pro` | Yes | Yes | Excellent | $$ |
| `black-forest-labs/flux.2-flex` | Yes | No | Good | $ |

## Model Details

### Google Gemini 3 Pro Image Preview
- **Model ID:** `google/gemini-3-pro-image-preview`
- **Best for:** High-quality generation, complex edits, scientific visualizations
- **Strengths:** Excellent prompt adherence, good at scientific/technical subjects
- **Limitations:** Preview model, may have rate limits

### FLUX.2 Pro (Black Forest Labs)
- **Model ID:** `black-forest-labs/flux.2-pro`
- **Best for:** Fast iteration, artistic images, photorealistic content
- **Strengths:** Fast generation, consistent quality, good editing
- **Limitations:** May require more specific prompts for technical accuracy

### FLUX.2 Flex (Black Forest Labs)
- **Model ID:** `black-forest-labs/flux.2-flex`
- **Best for:** Drafts, exploration, budget-conscious generation
- **Strengths:** Lower cost, reasonable quality
- **Limitations:** No editing support, may have quality variance

## Usage Examples

### Default (Gemini)
```bash
python {baseDir}/scripts/generate_image.py "Your prompt here"
```

### Specify FLUX.2 Pro
```bash
python {baseDir}/scripts/generate_image.py "Your prompt" --model "black-forest-labs/flux.2-pro"
```

### Specify FLUX.2 Flex (budget)
```bash
python {baseDir}/scripts/generate_image.py "Your prompt" --model "black-forest-labs/flux.2-flex"
```

## Decision Flow

```
What's your priority?
│
├─ Quality is critical (publication, hero image)
│  └─ Use: google/gemini-3-pro-image-preview
│
├─ Speed is important (iteration, drafts)
│  └─ Use: black-forest-labs/flux.2-pro
│
├─ Budget constrained
│  └─ Use: black-forest-labs/flux.2-flex
│
└─ Need to edit existing image
   └─ Use: google/gemini-3-pro-image-preview
      (or flux.2-pro as fallback)
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
- Gemini models: Higher quality, moderate cost
- FLUX models: Good balance of speed and cost
- Budget generation: Use flux.2-flex for exploration
