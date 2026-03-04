"""PIL diagram renderer for preview images."""
import math

from PIL import ImageDraw, ImageFont

from backend.src.constants.slide import DIAGRAM_TYPES, PIL_FONT_MAP

TIMELINE_LINE_Y = 480
TIMELINE_LEFT = 160
TIMELINE_RIGHT = 1760
TIMELINE_MARKER_R = 14

PROCESS_Y = 400
PROCESS_H = 180
PROCESS_LEFT = 160
PROCESS_RIGHT = 1760

CYCLE_CX = 960
CYCLE_CY = 560
CYCLE_R = 260
CYCLE_NODE_R = 80

PYR_TOP = 320
PYR_BOTTOM = 840
PYR_CX = 960
PYR_MAX_W = 1200

COMP_TOP = 300
COMP_COL_W = 700
COMP_GAP = 60
COMP_LEFT_X = 200

FONT_LABEL = 22
FONT_PERIOD = 22
FONT_SMALL = 18
FONT_COMP_TITLE = 28

WHITE = (255, 255, 255)


def _font(size: int, bold: bool = False, family: str = "gothic") -> ImageFont.FreeTypeFont:
    cfg = PIL_FONT_MAP.get(family, PIL_FONT_MAP["gothic"])
    key = "bold" if bold else "regular"
    try:
        return ImageFont.truetype(cfg[key], size)
    except (OSError, IOError):
        alt = "regular" if bold else "bold"
        try:
            return ImageFont.truetype(cfg[alt], size)
        except (OSError, IOError):
            return ImageFont.load_default()


def _center_text(
    draw: ImageDraw.Draw, text: str, cx: int, y: int,
    font: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, y), text, font=font, fill=fill)


def _shade(
    accent: tuple[int, int, int], i: int,
) -> tuple[int, int, int]:
    r, g, b = accent
    f = max(1.0 - i * 0.12, 0.3)
    return (max(int(r * f), 0), max(int(g * f), 0), max(int(b * f), 0))


def render_diagram(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    font_family: str = "gothic",
) -> None:
    dtype = chart_data.get("chart_type", "")
    if dtype not in DIAGRAM_TYPES:
        return
    renderer = _RENDERERS.get(dtype)
    if renderer:
        renderer(draw, img, chart_data, accent, text_color, font_family)


def _render_timeline(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    items = chart_data.get("items", [])
    if not items:
        return

    ly = TIMELINE_LINE_Y
    draw.line([(TIMELINE_LEFT, ly), (TIMELINE_RIGHT, ly)], fill=accent, width=4)

    n = len(items)
    total_w = TIMELINE_RIGHT - TIMELINE_LEFT
    for i, item in enumerate(items):
        cx = (
            TIMELINE_LEFT + (total_w * i // (n - 1))
            if n > 1
            else (TIMELINE_LEFT + TIMELINE_RIGHT) // 2
        )
        r = TIMELINE_MARKER_R
        draw.ellipse([(cx - r, ly - r), (cx + r, ly + r)], fill=accent)

        period = item.get("period", "")
        if period:
            _center_text(draw, period, cx, ly - 50, _font(FONT_PERIOD, True, ff), accent)

        label = item.get("label", "")
        if label:
            _center_text(draw, label, cx, ly + 25, _font(FONT_SMALL, False, ff), text_color)


def _render_process(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    items = chart_data.get("items", [])
    if not items:
        return

    n = len(items)
    total = PROCESS_RIGHT - PROCESS_LEFT
    arrow_w = 30 if n > 1 else 0
    box_w = (total - arrow_w * max(n - 1, 0)) // max(n, 1)

    for i, item in enumerate(items):
        x = PROCESS_LEFT + i * (box_w + arrow_w)
        c = _shade(accent, i)
        draw.rounded_rectangle(
            [(x, PROCESS_Y), (x + box_w, PROCESS_Y + PROCESS_H)],
            radius=12, fill=c,
        )

        label = item.get("label", "")
        if label:
            _center_text(
                draw, label, x + box_w // 2, PROCESS_Y + 30,
                _font(FONT_LABEL, True, ff), WHITE,
            )

        desc = item.get("description", "")
        if desc:
            _center_text(
                draw, desc, x + box_w // 2, PROCESS_Y + 80,
                _font(FONT_SMALL, False, ff), WHITE,
            )

        if i < n - 1:
            ax = x + box_w + arrow_w // 2
            ay = PROCESS_Y + PROCESS_H // 2
            draw.polygon(
                [(ax - 8, ay - 12), (ax + 8, ay), (ax - 8, ay + 12)],
                fill=accent,
            )


def _render_cycle(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    items = chart_data.get("items", [])
    if not items:
        return

    n = len(items)
    for i, item in enumerate(items):
        angle = 2 * math.pi * i / n - math.pi / 2
        nx = int(CYCLE_CX + CYCLE_R * math.cos(angle))
        ny = int(CYCLE_CY + CYCLE_R * math.sin(angle))
        r = CYCLE_NODE_R
        c = _shade(accent, i)
        draw.ellipse([(nx - r, ny - r), (nx + r, ny + r)], fill=c)

        label = item.get("label", "")
        if label:
            _center_text(draw, label, nx, ny - 10, _font(FONT_SMALL, True, ff), WHITE)

    for i in range(n):
        a1 = 2 * math.pi * i / n - math.pi / 2
        a2 = 2 * math.pi * ((i + 1) % n) / n - math.pi / 2
        mid_a = (a1 + a2) / 2
        mx = int(CYCLE_CX + (CYCLE_R - 40) * math.cos(mid_a))
        my = int(CYCLE_CY + (CYCLE_R - 40) * math.sin(mid_a))
        draw.ellipse([(mx - 4, my - 4), (mx + 4, my + 4)], fill=accent)


def _render_pyramid(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    items = chart_data.get("items", [])
    if not items:
        return

    n = len(items)
    total_h = PYR_BOTTOM - PYR_TOP
    row_h = total_h // n

    for i, item in enumerate(items):
        ratio = (i + 1) / n
        w = int(PYR_MAX_W * (0.3 + 0.7 * ratio))
        x = PYR_CX - w // 2
        y = PYR_TOP + i * row_h
        c = _shade(accent, i)
        draw.rounded_rectangle([(x, y), (x + w, y + row_h - 6)], radius=8, fill=c)

        label = item.get("label", "")
        if label:
            _center_text(
                draw, label, PYR_CX, y + row_h // 2 - 14,
                _font(FONT_LABEL, True, ff), WHITE,
            )


def _render_funnel(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    items = chart_data.get("items", [])
    if not items:
        return

    n = len(items)
    total_h = PYR_BOTTOM - PYR_TOP
    row_h = total_h // n

    for i, item in enumerate(items):
        ratio = 1.0 - (i / max(n, 1))
        w = int(PYR_MAX_W * (0.3 + 0.7 * ratio))
        x = PYR_CX - w // 2
        y = PYR_TOP + i * row_h
        c = _shade(accent, i)
        draw.rounded_rectangle([(x, y), (x + w, y + row_h - 6)], radius=8, fill=c)

        label = item.get("label", "")
        if label:
            _center_text(
                draw, label, PYR_CX, y + row_h // 2 - 14,
                _font(FONT_LABEL, True, ff), WHITE,
            )


def _render_comparison(
    draw: ImageDraw.Draw, img: object, chart_data: dict,
    accent: tuple[int, int, int], text_color: tuple[int, int, int],
    ff: str,
) -> None:
    left_d = chart_data.get("left", {})
    right_d = chart_data.get("right", {})
    rx = COMP_LEFT_X + COMP_COL_W + COMP_GAP

    for data, x, si in [(left_d, COMP_LEFT_X, 0), (right_d, rx, 2)]:
        title = data.get("title", "")
        c = _shade(accent, si)
        if title:
            draw.rounded_rectangle(
                [(x, COMP_TOP), (x + COMP_COL_W, COMP_TOP + 60)],
                radius=8, fill=c,
            )
            _center_text(
                draw, title, x + COMP_COL_W // 2, COMP_TOP + 14,
                _font(FONT_COMP_TITLE, True, ff), WHITE,
            )

        iy = COMP_TOP + 80
        for item_text in data.get("items", []):
            draw.text(
                (x + 20, iy), f"\u25cf {item_text}",
                font=_font(FONT_LABEL, False, ff), fill=text_color,
            )
            iy += 40


_RENDERERS = {
    "timeline": _render_timeline,
    "process": _render_process,
    "cycle": _render_cycle,
    "pyramid": _render_pyramid,
    "funnel": _render_funnel,
    "comparison": _render_comparison,
}
