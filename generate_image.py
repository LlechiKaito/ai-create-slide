import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types


def main():
    parser = argparse.ArgumentParser(description="Generate images using Gemini API (Imagen)")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", help="Output file path (default: output/<timestamp>.png)")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of images (1-4)")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: GEMINI_API_KEY is not set in .env", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    model = "imagen-4.0-fast-generate-001"
    print(f"Generating image with {model}: {args.prompt}")

    response = client.models.generate_images(
        model=model,
        prompt=args.prompt,
        config=types.GenerateImagesConfig(
            number_of_images=args.number,
            aspect_ratio=args.aspect_ratio,
        ),
    )

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, generated_image in enumerate(response.generated_images):
        if args.output:
            path = Path(args.output)
            if args.number > 1:
                path = path.with_stem(f"{path.stem}_{i+1}")
        else:
            suffix = f"_{i+1}" if args.number > 1 else ""
            path = output_dir / f"{timestamp}{suffix}.png"

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(generated_image.image.image_bytes)
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
