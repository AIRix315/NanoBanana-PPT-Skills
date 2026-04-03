#!/usr/bin/env python3
"""
PPT Generator - Generate PPT slide images using RunningHub API.

This script generates PPT slide images based on a slide plan and style template,
then creates an HTML viewer for playback.

Supports multiple image models:
- 全能图片V2 (Gemini 3.1 Flash) - Fast, cost-effective for drafts
- 全能图片PRO (Gemini 3 Pro) - High quality, 4K resolution for final output
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from rh_api import RunningHubClient, get_rh_client, RunningHubError


# =============================================================================
# Constants
# =============================================================================

DEFAULT_RESOLUTION = "2K"
DEFAULT_TEMPLATE_PATH = "templates/viewer.html"
OUTPUT_BASE_DIR = "outputs"

# Style template markers
TEMPLATE_START_MARKER = "## "
TEMPLATE_END_MARKER = "## "


# =============================================================================
# Environment Configuration
# =============================================================================

def find_and_load_env() -> bool:
    """
    Find and load .env file from multiple locations.

    Search priority:
    1. Current script directory
    2. Parent directories up to project root (containing .git or .env)
    3. Claude Code skill standard location (~/.claude/skills/ppt-generator/)

    Returns:
        True if .env file was found and loaded, False otherwise.
    """
    current_dir = Path(__file__).parent
    env_locations = [
        current_dir / ".env",
        *[parent / ".env" for parent in current_dir.parents],
        Path.home() / ".claude" / "skills" / "ppt-generator" / ".env",
    ]

    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"Loaded environment from: {env_path}")
            return True

        # Stop at project root if .git exists
        if env_path.parent != current_dir and (env_path.parent / ".git").exists():
            break

    # Fallback: try default loading from system environment
    load_dotenv(override=True)
    print("Warning: No .env file found, using system environment variables")
    return False


# =============================================================================
# Style Template
# =============================================================================

def load_style_template(style_path: str) -> str:
    """
    Load and parse style template file.

    Args:
        style_path: Path to the style template markdown file.

    Returns:
        Extracted base prompt template string.
    """
    with open(style_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract base prompt template section
    start_marker = "## "
    end_marker = "## "

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx + len(start_marker))

    if start_idx == -1 or end_idx == -1:
        print("Warning: Could not parse style template, using full content")
        return content

    return content[start_idx + len(start_marker):end_idx].strip()


# =============================================================================
# Prompt Generation
# =============================================================================

def generate_prompt(
    style_template: str,
    page_type: str,
    content_text: str,
    slide_number: int,
    total_slides: int,
) -> str:
    """
    Generate a prompt for a single slide.

    Args:
        style_template: Base style template text.
        page_type: Type of page (cover, data, content).
        content_text: Text content for the slide.
        slide_number: Current slide number (1-indexed).
        total_slides: Total number of slides.

    Returns:
        Complete prompt string for image generation.
    """
    prompt_parts = [style_template, "\n\n"]

    # Determine page type based on slide position or explicit type
    is_cover = page_type == "cover" or slide_number == 1
    is_data = page_type == "data" or slide_number == total_slides

    if is_cover:
        prompt_parts.append(
            f"""Please generate a cover page based on visual balance aesthetics.
Place a large complex 3D glass object in the center, overlaid with bold text:

{content_text}

Background with extended aurora waves."""
        )
    elif is_data:
        prompt_parts.append(
            f"""Please generate a data/summary page using split-screen design.
Left side: typeset the following text.
Right side: floating large glowing 3D data visualization:

{content_text}"""
        )
    else:
        prompt_parts.append(
            f"""Please generate a content page using Bento grid layout.
Organize the following content in modular rounded rectangle containers.
Container material must be frosted glass with blur effect:

{content_text}"""
        )

    return "".join(prompt_parts)


# =============================================================================
# Image Generation (RunningHub API)
# =============================================================================

def generate_slide(
    prompt: str,
    slide_number: int,
    output_dir: str,
    resolution: str = DEFAULT_RESOLUTION,
    model: str = "pro",
    client: Optional[RunningHubClient] = None,
) -> Optional[str]:
    """
    Generate a single PPT slide image using RunningHub API.

    Args:
        prompt: The generation prompt.
        slide_number: Slide number for filename.
        output_dir: Output directory path.
        resolution: Image resolution (1K, 2K, or 4K).
        model: Model type - "v2" (fast/draft) or "pro" (high quality).
        client: Optional RunningHub client instance.

    Returns:
        Path to saved image, or None if generation failed.
    """
    print(f"🎨 生成第 {slide_number} 页...")
    print(f"  模型: {'全能图片V2' if model == 'v2' else '全能图片PRO'}")
    print(f"  分辨率: {resolution}")

    try:
        # 初始化客户端（如果未提供）
        if client is None:
            client = get_rh_client()
        
        # 准备输出路径
        image_path = os.path.join(
            output_dir, "images", f"slide-{slide_number:02d}.png"
        )
        
        # 调用 RunningHub API
        client.generate_image(
            prompt=prompt,
            model=model,
            aspect_ratio="16:9",
            resolution=resolution,
            output_path=image_path,
        )
        
        print(f"✅ 第 {slide_number} 页已保存: {image_path}")
        return image_path

    except RunningHubError as e:
        print(f"❌ 第 {slide_number} 页失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 第 {slide_number} 页失败（未知错误）: {e}")
        return None


# =============================================================================
# Output Generation
# =============================================================================

def generate_viewer_html(
    output_dir: str,
    slide_count: int,
    template_path: str,
) -> str:
    """
    Generate HTML viewer for slides playback.

    Args:
        output_dir: Output directory path.
        slide_count: Total number of slides.
        template_path: Path to HTML template.

    Returns:
        Path to generated HTML file.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    # Generate image list
    slides_list = [f"'images/slide-{i:02d}.png'" for i in range(1, slide_count + 1)]

    # Replace placeholder
    html_content = html_template.replace(
        "/* IMAGE_LIST_PLACEHOLDER */",
        ",\n            ".join(slides_list),
    )

    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"  Viewer HTML generated: {html_path}")
    return html_path


def save_prompts(output_dir: str, prompts_data: Dict[str, Any]) -> str:
    """
    Save all prompts to JSON file.

    Args:
        output_dir: Output directory path.
        prompts_data: Dictionary containing all prompts and metadata.

    Returns:
        Path to saved JSON file.
    """
    prompts_path = os.path.join(output_dir, "prompts.json")
    with open(prompts_path, "w", encoding="utf-8") as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
    print(f"  Prompts saved: {prompts_path}")
    return prompts_path


# =============================================================================
# Main Entry Point
# =============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="PPT Generator - Generate PPT images using RunningHub API (国内中转)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # 草稿模式（快速、低成本）
  python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --draft

  # 最终模式（高质量）
  python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model pro --resolution 4K

  # 指定模型
  python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model v2

Environment variables:
  RH_API_KEY: RunningHub API key (required)
    Get from: https://www.runninghub.cn/enterprise-api/sharedApi
        """,
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to slides plan JSON file (generated by Skill)",
    )
    parser.add_argument(
        "--style",
        required=True,
        help="Path to style template file",
    )
    parser.add_argument(
        "--resolution",
        choices=["1K", "2K", "4K"],
        default=DEFAULT_RESOLUTION,
        help=f"Image resolution (default: {DEFAULT_RESOLUTION})",
    )
    parser.add_argument(
        "--model",
        choices=["v2", "pro"],
        default="pro",
        help=(
            "Image generation model:\n"
            "  v2: 全能图片V2 (Gemini 3.1 Flash) - Fast, cost-effective\n"
            "  pro: 全能图片PRO (Gemini 3 Pro) - High quality, 4K (default)"
        ),
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Draft mode shortcut: use v2 model + 1K resolution for fast generation",
    )
    parser.add_argument(
        "--output",
        help="Output directory path (default: outputs/TIMESTAMP)",
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE_PATH,
        help=f"HTML template path (default: {DEFAULT_TEMPLATE_PATH})",
    )

    return parser


def main() -> None:
    """Main entry point for PPT generation."""
    # Load environment variables
    find_and_load_env()

    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle draft mode
    model = "v2" if args.draft else args.model
    resolution = "1K" if args.draft else args.resolution

    # Load slides plan
    with open(args.plan, "r", encoding="utf-8") as f:
        slides_plan = json.load(f)

    # Load style template
    style_template = load_style_template(args.style)

    # Create output directory
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{OUTPUT_BASE_DIR}/{timestamp}"

    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)

    # Print configuration
    slides = slides_plan["slides"]
    total_slides = len(slides)

    print("=" * 60)
    print("PPT Generator - RunningHub API (国内中转)")
    print("=" * 60)
    print(f"风格: {args.style}")
    print(f"模型: {'全能图片V2 (草稿模式)' if args.draft else '全能图片PRO' if model == 'pro' else '全能图片V2'}")
    print(f"分辨率: {resolution}")
    print(f"总页数: {total_slides}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    print()

    # Initialize RunningHub client
    try:
        client = get_rh_client()
    except RunningHubError as e:
        print(f"❌ RunningHub 客户端初始化失败: {e}")
        sys.exit(1)

    # Initialize prompts data
    prompts_data: Dict[str, Any] = {
        "metadata": {
            "title": slides_plan.get("title", "Untitled Presentation"),
            "total_slides": total_slides,
            "resolution": resolution,
            "model": model,
            "style": args.style,
            "generated_at": datetime.now().isoformat(),
        },
        "slides": [],
    }

    # Generate each slide
    for slide_info in slides:
        slide_number = slide_info["slide_number"]
        page_type = slide_info.get("page_type", "content")
        content_text = slide_info["content"]

        # Generate prompt
        prompt = generate_prompt(
            style_template,
            page_type,
            content_text,
            slide_number,
            total_slides,
        )

        # Generate image
        image_path = generate_slide(
            prompt,
            slide_number,
            output_dir,
            resolution,
            model,
            client,  # Reuse client for all slides
        )

        # Record prompt data
        prompts_data["slides"].append({
            "slide_number": slide_number,
            "page_type": page_type,
            "content": content_text,
            "prompt": prompt,
            "image_path": image_path,
        })

        print()

    # Save prompts
    save_prompts(output_dir, prompts_data)

    # Generate viewer HTML
    generate_viewer_html(output_dir, total_slides, args.template)

    # Print completion summary
    print()
    print("=" * 60)
    print("✅ 生成完成！")
    print("=" * 60)
    print(f"📁 输出目录: {output_dir}")
    print(f"🖼️ PPT 图片: {os.path.join(output_dir, 'images')}")
    print(f"🎬 播放网页: {os.path.join(output_dir, 'index.html')}")
    print()
    print("打开播放网页：")
    print(f"  open {os.path.join(output_dir, 'index.html')}")
    print()


if __name__ == "__main__":
    main()
