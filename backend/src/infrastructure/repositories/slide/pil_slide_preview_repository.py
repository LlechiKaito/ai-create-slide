import base64
import io

from PIL import Image, ImageDraw, ImageFont

from backend.src.constants.slide import (
    PREVIEW_ACCENT_BAR,
    PREVIEW_ACCENT_LINE_W,
    PREVIEW_BULLET_INDENT,
    PREVIEW_CONTENT_START_Y,
    PREVIEW_FONT_AUTHOR,
    PREVIEW_FONT_BODY,
    PREVIEW_FONT_BULLET,
    PREVIEW_FONT_BULLET_MARKER,
    PREVIEW_FONT_DECK_TITLE,
    PREVIEW_FONT_PAGE_NUM,
    PREVIEW_FONT_SLIDE_TITLE,
    PREVIEW_FONT_SUBTITLE,
    PREVIEW_HEIGHT,
    PREVIEW_LINE_SPACING,
    PREVIEW_MARGIN_X,
    PREVIEW_MAX_TEXT_WIDTH,
    PREVIEW_TITLE_BLOCK_H,
    PREVIEW_WIDTH,
)
from backend.src.domain.commons.result import Result, success
from backend.src.domain.repositories.slide.slide_preview_repository import (
    SlidePreviewRepository,
)

DEFAULT_COLOR_WHITE = (255, 255, 255)
DEFAULT_COLOR_DARK = (50, 50, 50)
DEFAULT_COLOR_ORANGE = (240, 130, 40)
COLOR_LIGHT_GRAY = (180, 180, 180)

FONT_PATH_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_PATH_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
ACCENT_LINE_WIDTH = 3
TITLE_ACCENT_LINE_WIDTH = 4
ACCENT_LINE_LENGTH = 200
IMAGE_SIZE = 520
IMAGE_MARGIN = 40
IMAGE_BORDER_RADIUS = 20


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


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = [FONT_PATH_BOLD, FONT_PATH_REGULAR]
    if not bold:
        paths.reverse()
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
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


def _decode_and_place_image(base: Image.Image, image_data: str) -> None:
    raw = base64.b64decode(image_data)
    asset = Image.open(io.BytesIO(raw)).convert("RGBA")
    asset = asset.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)

    mask = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (IMAGE_SIZE, IMAGE_SIZE)],
        radius=IMAGE_BORDER_RADIUS, fill=255,
    )

    x = PREVIEW_WIDTH - PREVIEW_MARGIN_X - IMAGE_SIZE
    y = (PREVIEW_HEIGHT - IMAGE_SIZE) // 2
    base.paste(asset, (x, y), mask)


def _render_title_slide(
    deck_title: str, author: str,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    bg: tuple[int, int, int],
) -> bytes:
    img, draw = _create_base(accent, bg)

    cy = (PREVIEW_HEIGHT - PREVIEW_TITLE_BLOCK_H) // 2
    x_start = (PREVIEW_WIDTH - PREVIEW_ACCENT_LINE_W) // 2

    draw.line(
        [(x_start, cy), (x_start + PREVIEW_ACCENT_LINE_W, cy)],
        fill=accent, width=ACCENT_LINE_WIDTH,
    )
    _draw_centered(
        draw, deck_title, cy + 30,
        _get_font(PREVIEW_FONT_DECK_TITLE, bold=True), text_color,
    )
    if author:
        _draw_centered(
            draw, author, cy + 140,
            _get_font(PREVIEW_FONT_AUTHOR), COLOR_LIGHT_GRAY,
        )
    draw.line(
        [(x_start, cy + 200), (x_start + PREVIEW_ACCENT_LINE_W, cy + 200)],
        fill=accent, width=ACCENT_LINE_WIDTH,
    )

    return _image_to_bytes(img)


def _draw_slide_header(
    draw: ImageDraw.Draw, slide: dict, index: int,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
) -> int:
    draw.text(
        (PREVIEW_WIDTH - 100, PREVIEW_HEIGHT - 60),
        str(index), font=_get_font(PREVIEW_FONT_PAGE_NUM), fill=COLOR_LIGHT_GRAY,
    )
    y = PREVIEW_CONTENT_START_Y
    draw.text(
        (PREVIEW_MARGIN_X, y), slide.get("title", ""),
        font=_get_font(PREVIEW_FONT_SLIDE_TITLE, bold=True), fill=text_color,
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
            font=_get_font(PREVIEW_FONT_SUBTITLE), fill=accent,
        )
        y += 50
    return y + 20


def _draw_slide_body(
    draw: ImageDraw.Draw, slide: dict, y: int, has_image: bool,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
) -> None:
    text_area_w = PREVIEW_WIDTH - PREVIEW_MARGIN_X * 2
    if has_image:
        text_area_w = text_area_w - IMAGE_SIZE - IMAGE_MARGIN

    content = slide.get("content", "")
    if content:
        y = _draw_wrapped(
            draw, content, PREVIEW_MARGIN_X, y,
            _get_font(PREVIEW_FONT_BODY), text_color, max_width=text_area_w,
        )
        y += 30

    for bp in slide.get("bullet_points", []):
        if y > PREVIEW_HEIGHT - 80:
            break
        draw.text(
            (PREVIEW_MARGIN_X, y), "\u25cf",
            font=_get_font(PREVIEW_FONT_BULLET_MARKER), fill=accent,
        )
        y = _draw_wrapped(
            draw, bp, PREVIEW_MARGIN_X + PREVIEW_BULLET_INDENT, y,
            _get_font(PREVIEW_FONT_BULLET), text_color,
            max_width=text_area_w - PREVIEW_BULLET_INDENT,
        )
        y += 10


def _render_content_slide(
    slide: dict, index: int,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    bg: tuple[int, int, int],
) -> bytes:
    img, draw = _create_base(accent, bg)
    image_data = slide.get("image_data", "")
    has_image = bool(image_data)

    y = _draw_slide_header(draw, slide, index, accent, text_color)
    _draw_slide_body(draw, slide, y, has_image, accent, text_color)

    if has_image:
        _decode_and_place_image(img, image_data)

    return _image_to_bytes(img)


class PilSlidePreviewRepository(SlidePreviewRepository):
    def render_preview_images(
        self, deck_title: str, author: str, slides: list[dict],
        color_config: dict | None = None,
    ) -> Result[list[bytes], Exception]:
        accent, text_color, bg = _resolve_colors(color_config)

        images: list[bytes] = []
        images.append(_render_title_slide(deck_title, author, accent, text_color, bg))
        for i, slide in enumerate(slides, start=2):
            images.append(_render_content_slide(slide, i, accent, text_color, bg))
        return success(images)
