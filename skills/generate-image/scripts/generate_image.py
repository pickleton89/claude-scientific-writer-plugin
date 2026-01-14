#!/usr/bin/env python3
"""
Generate and edit images using OpenRouter API.

Default model: google/gemini-3-pro-image-preview
- Supports generation, editing, and inpainting
- Best overall quality for scientific visualizations

For image editing, provide an input image along with an editing prompt.

Note: FLUX.2 models are deprecated. Use Gemini 3 Pro for all use cases.
"""

import sys
import json
import base64
import argparse
from pathlib import Path
from typing import Optional

# Import model validation utilities
try:
    from utils.models import validate_model, DEFAULT_MODEL
except ImportError:
    # Fallback if running from different directory - validation will be skipped
    # but core functionality still works
    validate_model = None
    DEFAULT_MODEL = "google/gemini-3-pro-image-preview"

# Import shared API utilities
try:
    # When running from within skills directory structure
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from api_utils import load_api_key, get_api_config, make_openrouter_request, APIError
except ImportError:
    # Fallback: shared module not available, will use inline implementation
    load_api_key = None
    get_api_config = None
    make_openrouter_request = None
    APIError = None


def load_image_as_base64(image_path: str) -> str:
    """Load an image file and return it as a base64 data URL."""
    path = Path(image_path)
    if not path.exists():
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Determine MIME type from extension
    ext = path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime_type = mime_types.get(ext, 'image/png')
    
    with open(path, 'rb') as f:
        image_data = f.read()
    
    base64_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{base64_data}"


def save_base64_image(base64_data: str, output_path: str) -> None:
    """Save base64 encoded image to file."""
    # Remove data URL prefix if present
    if ',' in base64_data:
        base64_data = base64_data.split(',', 1)[1]

    # Decode and save
    image_data = base64.b64decode(base64_data)
    with open(output_path, 'wb') as f:
        f.write(image_data)


def generate_image(
    prompt: str,
    model: str = "google/gemini-3-pro-image-preview",
    output_path: str = "generated_image.png",
    api_key: Optional[str] = None,
    input_image: Optional[str] = None
) -> dict:
    """
    Generate or edit an image using OpenRouter API.

    Args:
        prompt: Text description of the image to generate, or editing instructions
        model: OpenRouter model ID (default: google/gemini-3-pro-image-preview)
        output_path: Path to save the generated image
        api_key: OpenRouter API key (will check .env if not provided)
        input_image: Path to an input image for editing (optional)

    Returns:
        dict: Response from OpenRouter API
    """
    # Validate model and check for deprecation
    if validate_model is not None:
        validation = validate_model(model, warn_deprecated=False)
        if not validation.valid:
            print(f"⚠️  {validation.error}")
            if validation.suggestion:
                print(f"   {validation.suggestion}")
            sys.exit(1)
        if validation.deprecation_warning:
            print(f"⚠️  Deprecation Warning: {validation.deprecation_warning}")
            print(f"   Continuing with {model}, but consider switching to {DEFAULT_MODEL}")

    # Load API key using shared utilities if available
    if load_api_key is not None:
        resolved_api_key = load_api_key(
            explicit_key=api_key,
            caller_file=__file__
        )
    else:
        # Fallback: only use explicit key or environment variable
        import os
        resolved_api_key = api_key or os.environ.get("OPENROUTER_API_KEY")

    if not resolved_api_key:
        print("❌ Error: OPENROUTER_API_KEY not found!")
        print("\nPlease create a .env file in your project directory with:")
        print("OPENROUTER_API_KEY=your-api-key-here")
        print("\nOr set the environment variable:")
        print("export OPENROUTER_API_KEY=your-api-key-here")
        print("\nGet your API key from: https://openrouter.ai/keys")
        sys.exit(1)

    # Determine if this is generation or editing
    is_editing = input_image is not None

    if is_editing:
        print(f"✏️ Editing image with model: {model}")
        print(f"📷 Input image: {input_image}")
        print(f"📝 Edit prompt: {prompt}")

        # Load input image as base64
        image_data_url = load_image_as_base64(input_image)

        # Build multimodal message content for image editing
        message_content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url
                }
            }
        ]
    else:
        print(f"🎨 Generating image with model: {model}")
        print(f"📝 Prompt: {prompt}")
        message_content = prompt

    # Build messages for API request
    messages = [
        {
            "role": "user",
            "content": message_content
        }
    ]

    # Make API request using shared utilities if available
    if make_openrouter_request is not None and get_api_config is not None:
        try:
            config = get_api_config(api_key=resolved_api_key)
            result = make_openrouter_request(
                config=config,
                model=model,
                messages=messages,
                modalities=["image", "text"]
            )
        except APIError as e:
            print(f"❌ API Error ({e.status_code}): {e.detail}")
            sys.exit(1)
        except ImportError as e:
            # Handles case where shared module loads but requests isn't installed
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Fallback: make request directly
        try:
            import requests
        except ImportError:
            print("Error: 'requests' library not found. Install with: pip install requests")
            sys.exit(1)

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {resolved_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "modalities": ["image", "text"]
            }
        )

        # Check for errors
        if response.status_code != 200:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            sys.exit(1)

        result = response.json()

    # Extract and save image
    if result.get("choices"):
        message = result["choices"][0]["message"]

        # Handle both 'images' and 'content' response formats
        images = []

        if message.get("images"):
            images = message["images"]
        elif message.get("content"):
            # Some models return content as array with image parts
            content = message["content"]
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "image":
                        images.append(part)

        if images:
            # Save the first image
            image = images[0]
            if "image_url" in image:
                image_url = image["image_url"]["url"]
                save_base64_image(image_url, output_path)
                print(f"✅ Image saved to: {output_path}")
            elif "url" in image:
                save_base64_image(image["url"], output_path)
                print(f"✅ Image saved to: {output_path}")
            else:
                print(f"⚠️ Unexpected image format: {image}")
        else:
            print("⚠️ No image found in response")
            if message.get("content"):
                print(f"Response content: {message['content']}")
    else:
        print("❌ No choices in response")
        print(f"Response: {json.dumps(result, indent=2)}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an image
  python generate_image.py "A beautiful sunset over mountains"

  # Specify output path
  python generate_image.py "Abstract art" --output my_image.png

  # Edit an existing image
  python generate_image.py "Make the sky purple" --input photo.jpg --output edited.png

  # Edit with specific instructions
  python generate_image.py "Add a hat to the person" --input portrait.png --output edited.png

Default model: google/gemini-3-pro-image-preview
  - High quality generation and editing
  - Supports inpainting
  - Best for scientific visualizations

Note: FLUX.2 models are deprecated and will show warnings if used.
        """
    )

    parser.add_argument(
        "prompt",
        type=str,
        help="Text description of the image to generate, or editing instructions"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default="google/gemini-3-pro-image-preview",
        help="OpenRouter model ID (default: google/gemini-3-pro-image-preview)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="generated_image.png",
        help="Output file path (default: generated_image.png)"
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input image path for editing (enables edit mode)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenRouter API key (will check .env if not provided)"
    )

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        model=args.model,
        output_path=args.output,
        api_key=args.api_key,
        input_image=args.input
    )


if __name__ == "__main__":
    main()
