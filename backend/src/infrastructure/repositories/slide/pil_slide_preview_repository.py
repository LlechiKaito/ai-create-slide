import base64
import io
import logging

import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from backend.src.constants.slide import (
    DEFAULT_CONTENT_GAP,
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE_LEVEL,
    DEFAULT_IMAGE_SIZE,
    DIAGRAM_TYPES,
    PIL_FONT_MAP,
    PREVIEW_ACCENT_BAR,
    PREVIEW_ACCENT_LINE_W,
    PREVIEW_BULLET_INDENT,
    PREVIEW_CONTENT_GAPS,
    PREVIEW_CONTENT_START_Y,
    PREVIEW_FONT_PAGE_NUM,
    PREVIEW_HEIGHT,
    PREVIEW_FONT_SIZE_ACCENT,
    PREVIEW_FONT_SIZE_BODY,
    PREVIEW_FONT_SIZE_TITLE,
    PREVIEW_IMAGE_SIZES,
    PREVIEW_LINE_SPACING,
    PREVIEW_MARGIN_X,
    PREVIEW_MAX_TEXT_WIDTH,
    PREVIEW_TITLE_BLOCK_H,
    PREVIEW_WIDTH,
    SUPPORTED_CHART_TYPES,
)
from backend.src.domain.commons.result import Result, success
from backend.src.domain.repositories.slide.slide_preview_repository import (
    SlidePreviewRepository,
)
from backend.src.infrastructure.repositories.slide.pil_diagram_renderer import (
    render_diagram,
)

matplotlib.use("Agg")
logger = logging.getLogger(__name__)

DEFAULT_COLOR_WHITE = (255, 255, 255)
DEFAULT_COLOR_DARK = (50, 50, 50)
DEFAULT_COLOR_ORANGE = (240, 130, 40)
COLOR_LIGHT_GRAY = (180, 180, 180)
CHART_SIZE = 520
CHART_MARGIN = 40

ACCENT_LINE_WIDTH = 3
TITLE_ACCENT_LINE_WIDTH = 4
ACCENT_LINE_LENGTH = 200
IMAGE_BORDER_RADIUS = 20


def _resolve_preview_font_sizes(cfg: dict) -> dict[str, int]:
    t = cfg.get("font_size_title", DEFAULT_FONT_SIZE_LEVEL)
    b = cfg.get("font_size_body", DEFAULT_FONT_SIZE_LEVEL)
    a = cfg.get("font_size_accent", DEFAULT_FONT_SIZE_LEVEL)
    title = PREVIEW_FONT_SIZE_TITLE.get(t, PREVIEW_FONT_SIZE_TITLE["medium"])
    body = PREVIEW_FONT_SIZE_BODY.get(b, PREVIEW_FONT_SIZE_BODY["medium"])
    accent = PREVIEW_FONT_SIZE_ACCENT.get(a, PREVIEW_FONT_SIZE_ACCENT["medium"])
    return {
        "deck_title": int(title * 1.5),
        "author": int(accent * 1.3),
        "title": title,
        "subtitle": accent,
        "body": body,
        "bullet": max(body - 2, 18),
        "bullet_marker": max(body - 8, 14),
        "page_num": PREVIEW_FONT_PAGE_NUM,
    }


def _hex_to_tuple(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _resolve_colors(
    color_config: dict | None,
) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    if not color_config:
        return DEFAULT_COLOR_ORANGE, DEFAULT_COLOR_DARK, DEFAULT_COLOR_WHITE
    accent = _hex_to_tuple(color_config.get("accent", "#F08228"))
    text = _hex_to_tuple(color_config.get("text", "#323232"))
    bg = _hex_to_tuple(color_config.get("background", "#FFFFFF"))
    return accent, text, bg


def _get_font(
    size: int, bold: bool = False, font_family: str = "gothic",
) -> ImageFont.FreeTypeFont:
    cfg = PIL_FONT_MAP.get(font_family, PIL_FONT_MAP["gothic"])
    key = "bold" if bold else "regular"
    try:
        return ImageFont.truetype(cfg[key], size)
    except (OSError, IOError):
        alt = "regular" if bold else "bold"
        try:
            return ImageFont.truetype(cfg[alt], size)
        except (OSError, IOError):
            return ImageFont.load_default()


def _create_base(
    accent: tuple[int, int, int], bg: tuple[int, int, int],
) -> tuple[Image.Image, ImageDraw.Draw]:
    img = Image.new("RGB", (PREVIEW_WIDTH, PREVIEW_HEIGHT), bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (PREVIEW_WIDTH, PREVIEW_ACCENT_BAR)], fill=accent)
    draw.rectangle(
        [(0, PREVIEW_HEIGHT - PREVIEW_ACCENT_BAR), (PREVIEW_WIDTH, PREVIEW_HEIGHT)],
        fill=accent,
    )
    return img, draw


def _draw_centered(
    draw: ImageDraw.Draw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (PREVIEW_WIDTH - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_wrapped(
    draw: ImageDraw.Draw,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    max_width: int = PREVIEW_MAX_TEXT_WIDTH,
) -> int:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for char in paragraph:
            test = line + char
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                lines.append(line)
                line = char
            else:
                line = test
        lines.append(line)

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + PREVIEW_LINE_SPACING
    return y


def _image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _decode_and_place_image(
    base: Image.Image, image_data: str,
    image_size: str = DEFAULT_IMAGE_SIZE,
) -> None:
    size_px = PREVIEW_IMAGE_SIZES.get(image_size, PREVIEW_IMAGE_SIZES[DEFAULT_IMAGE_SIZE])
    raw = base64.b64decode(image_data)
    asset = Image.open(io.BytesIO(raw)).convert("RGBA")
    asset = asset.resize((size_px, size_px), Image.LANCZOS)

    mask = Image.new("L", (size_px, size_px), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (size_px, size_px)],
        radius=IMAGE_BORDER_RADIUS, fill=255,
    )

    x = PREVIEW_WIDTH - PREVIEW_MARGIN_X - size_px
    y = (PREVIEW_HEIGHT - size_px) // 2
    base.paste(asset, (x, y), mask)


def _render_title_slide(
    deck_title: str, author: str,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    bg: tuple[int, int, int], font_family: str = "gothic",
    font_sizes: dict | None = None,
) -> bytes:
    fs = font_sizes or _resolve_preview_font_sizes({})
    img, draw = _create_base(accent, bg)

    cy = (PREVIEW_HEIGHT - PREVIEW_TITLE_BLOCK_H) // 2
    x_start = (PREVIEW_WIDTH - PREVIEW_ACCENT_LINE_W) // 2

    draw.line(
        [(x_start, cy), (x_start + PREVIEW_ACCENT_LINE_W, cy)],
        fill=accent, width=ACCENT_LINE_WIDTH,
    )
    _draw_centered(
        draw, deck_title, cy + 30,
        _get_font(fs["deck_title"], bold=True, font_family=font_family),
        text_color,
    )
    if author:
        _draw_centered(
            draw, author, cy + 140,
            _get_font(fs["author"], font_family=font_family),
            COLOR_LIGHT_GRAY,
        )
    draw.line(
        [(x_start, cy + 200), (x_start + PREVIEW_ACCENT_LINE_W, cy + 200)],
        fill=accent, width=ACCENT_LINE_WIDTH,
    )

    return _image_to_bytes(img)


def _draw_slide_header(
    draw: ImageDraw.Draw, slide: dict, index: int,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    font_family: str = "gothic", font_sizes: dict | None = None,
) -> int:
    fs = font_sizes or _resolve_preview_font_sizes({})
    draw.text(
        (PREVIEW_WIDTH - 100, PREVIEW_HEIGHT - 60),
        str(index),
        font=_get_font(fs["page_num"], font_family=font_family),
        fill=COLOR_LIGHT_GRAY,
    )
    y = PREVIEW_CONTENT_START_Y
    draw.text(
        (PREVIEW_MARGIN_X, y), slide.get("title", ""),
        font=_get_font(fs["title"], bold=True, font_family=font_family),
        fill=text_color,
    )
    y += 70
    draw.line(
        [(PREVIEW_MARGIN_X, y), (PREVIEW_MARGIN_X + ACCENT_LINE_LENGTH, y)],
        fill=accent, width=TITLE_ACCENT_LINE_WIDTH,
    )
    y += 30
    subtitle = slide.get("subtitle", "")
    if subtitle:
        draw.text(
            (PREVIEW_MARGIN_X, y), subtitle,
            font=_get_font(fs["subtitle"], font_family=font_family),
            fill=accent,
        )
        y += 50
    return y + 20


def _draw_slide_body(
    draw: ImageDraw.Draw, slide: dict, y: int,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    font_family: str = "gothic",
    image_size_px: int = 0, image_gap_px: int = 0,
    font_sizes: dict | None = None,
) -> None:
    fs = font_sizes or _resolve_preview_font_sizes({})
    text_area_w = PREVIEW_WIDTH - PREVIEW_MARGIN_X * 2
    if image_size_px > 0:
        text_area_w = text_area_w - image_size_px - image_gap_px

    content = slide.get("content", "")
    if content:
        y = _draw_wrapped(
            draw, content, PREVIEW_MARGIN_X, y,
            _get_font(fs["body"], font_family=font_family),
            text_color, max_width=text_area_w,
        )
        y += 30

    for bp in slide.get("bullet_points", []):
        if y > PREVIEW_HEIGHT - 80:
            break
        draw.text(
            (PREVIEW_MARGIN_X, y), "\u25cf",
            font=_get_font(fs["bullet_marker"], font_family=font_family),
            fill=accent,
        )
        y = _draw_wrapped(
            draw, bp, PREVIEW_MARGIN_X + PREVIEW_BULLET_INDENT, y,
            _get_font(fs["bullet"], font_family=font_family),
            text_color,
            max_width=text_area_w - PREVIEW_BULLET_INDENT,
        )
        y += 10


def _render_chart_image(
    chart_data: dict, accent: tuple[int, int, int],
) -> Image.Image | None:
    chart_type = chart_data.get("chart_type", "column")
    if chart_type not in SUPPORTED_CHART_TYPES:
        chart_type = "column"
    categories = chart_data.get("categories", [])
    series_list = chart_data.get("series", [])
    if not categories or not series_list:
        return None

    dpi = 100
    fig_size = CHART_SIZE / dpi
    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)

    try:
        if chart_type == "pie":
            values = series_list[0].get("values", [])
            ax.pie(values, labels=categories, autopct="%1.0f%%", startangle=90)
        elif chart_type == "bar":
            import numpy as np
            y_pos = np.arange(len(categories))
            bar_h = 0.8 / len(series_list)
            for i, s in enumerate(series_list):
                ax.barh(y_pos + i * bar_h, s.get("values", []), bar_h,
                        label=s.get("name", ""), alpha=0.8 + i * 0.05)
            ax.set_yticks(y_pos + bar_h * (len(series_list) - 1) / 2)
            ax.set_yticklabels(categories)
        elif chart_type == "line":
            for s in series_list:
                ax.plot(categories, s.get("values", []), marker="o", label=s.get("name", ""))
        else:
            import numpy as np
            x_pos = np.arange(len(categories))
            bar_w = 0.8 / len(series_list)
            for i, s in enumerate(series_list):
                ax.bar(x_pos + i * bar_w, s.get("values", []), bar_w,
                       label=s.get("name", ""), alpha=0.8 + i * 0.05)
            ax.set_xticks(x_pos + bar_w * (len(series_list) - 1) / 2)
            ax.set_xticklabels(categories, fontsize=8)

        chart_title = chart_data.get("title", "")
        if chart_title:
            ax.set_title(chart_title, fontsize=11)
        if len(series_list) > 1 and chart_type != "pie":
            ax.legend(fontsize=8)

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="PNG", bbox_inches="tight", facecolor="white")
        buf.seek(0)
        return Image.open(buf).convert("RGBA")
    except Exception:
        logger.warning("Failed to render chart preview", exc_info=True)
        return None
    finally:
        plt.close(fig)


def _place_chart_on_slide(base: Image.Image, chart_img: Image.Image) -> None:
    chart_img = chart_img.resize((CHART_SIZE, CHART_SIZE), Image.LANCZOS)
    x = PREVIEW_WIDTH - PREVIEW_MARGIN_X - CHART_SIZE
    y = (PREVIEW_HEIGHT - CHART_SIZE) // 2
    base.paste(chart_img, (x, y), chart_img)


def _render_content_slide(
    slide: dict, index: int,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    bg: tuple[int, int, int], font_family: str = "gothic",
    image_size: str = DEFAULT_IMAGE_SIZE, content_gap: str = DEFAULT_CONTENT_GAP,
    font_sizes: dict | None = None,
) -> bytes:
    img, draw = _create_base(accent, bg)
    image_data = slide.get("image_data", "")
    chart_data = slide.get("chart_data")
    is_diagram = (
        bool(chart_data)
        and chart_data.get("chart_type") in DIAGRAM_TYPES
    )
    has_chart = bool(chart_data) and not is_diagram
    has_image = bool(image_data) and not has_chart and not is_diagram

    image_size_px = 0
    image_gap_px = 0
    if has_image:
        image_size_px = PREVIEW_IMAGE_SIZES.get(image_size, PREVIEW_IMAGE_SIZES[DEFAULT_IMAGE_SIZE])
        image_gap_px = PREVIEW_CONTENT_GAPS.get(content_gap, PREVIEW_CONTENT_GAPS[DEFAULT_CONTENT_GAP])
    elif has_chart:
        image_size_px = CHART_SIZE
        image_gap_px = CHART_MARGIN

    y = _draw_slide_header(draw, slide, index, accent, text_color, font_family, font_sizes)
    _draw_slide_body(
        draw, slide, y, accent, text_color, font_family,
        image_size_px, image_gap_px, font_sizes,
    )

    if is_diagram:
        render_diagram(draw, img, chart_data, accent, text_color, font_family)
    elif has_chart:
        chart_img = _render_chart_image(chart_data, accent)
        if chart_img:
            _place_chart_on_slide(img, chart_img)
    elif has_image:
        _decode_and_place_image(img, image_data, image_size)

    return _image_to_bytes(img)


class PilSlidePreviewRepository(SlidePreviewRepository):
    def render_preview_images(
        self, deck_title: str, author: str, slides: list[dict],
        color_config: dict | None = None,
    ) -> Result[list[bytes], Exception]:
        accent, text_color, bg = _resolve_colors(color_config)
        cfg = color_config or {}
        font_family = cfg.get("font_family", DEFAULT_FONT_FAMILY)
        image_size = cfg.get("image_size", DEFAULT_IMAGE_SIZE)
        content_gap = cfg.get("content_gap", DEFAULT_CONTENT_GAP)
        font_sizes = _resolve_preview_font_sizes(cfg)

        images: list[bytes] = []
        images.append(
            _render_title_slide(
                deck_title, author, accent, text_color, bg, font_family, font_sizes,
            ),
        )
        for i, slide in enumerate(slides, start=2):
            images.append(
                _render_content_slide(
                    slide, i, accent, text_color, bg, font_family,
                    image_size, content_gap, font_sizes,
                ),
            )
        return success(images)
