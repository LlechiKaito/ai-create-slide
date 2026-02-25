from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

WIDTH, HEIGHT = 1920, 1080
OUTPUT_DIR = Path("output/slides")
ASSETS_DIR = Path("output/assets")

# Colors — white bg, dark gray text, orange accent
BG_COLOR = (255, 255, 255)
DARK = (50, 50, 50)
ORANGE = (240, 130, 40)
LIGHT_GRAY = (220, 220, 220)

# ── Consistent spacing (based on slide 4) ──
SUB_TITLE_Y = 50
MAIN_TITLE_Y = 95
TITLE_LINE_Y = 175
CONTENT_Y = 220
CONTENT_GAP = 50
SECTION_GAP = 35
HEADING_GAP = 10
IMG_SIZE = 340
LINE_W = 500


def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    if not bold:
        paths.reverse()
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def white_bg():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ORANGE)
    draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=ORANGE)
    return img, draw


def draw_accent_line(draw, y, width=LINE_W):
    x_start = (WIDTH - width) // 2
    draw.line([(x_start, y), (x_start + width, y)], fill=ORANGE, width=3)


def draw_title_block(draw, sub, main):
    draw_centered(draw, sub, SUB_TITLE_Y, get_font(32), ORANGE)
    draw_centered(draw, main, MAIN_TITLE_Y, get_font(60, bold=True), DARK)
    draw_accent_line(draw, TITLE_LINE_Y)


def draw_centered(draw, text, y, font, fill=DARK):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_wrapped(draw, text, x, y, font, fill=DARK, max_width=1400):
    lines = []
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
        y += (bbox[3] - bbox[1]) + 14
    return y


def place_image_wide(base, asset_path, x, y, width, height, rounded=True):
    """Place a wide (non-square) image."""
    try:
        asset = Image.open(asset_path).convert("RGBA")
        asset = asset.resize((width, height), Image.LANCZOS)
        if rounded:
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=20, fill=255)
            base.paste(asset, (x, y), mask)
        else:
            base.paste(asset, (x, y))
    except FileNotFoundError:
        pass


def place_image(base, asset_path, x, y, size, rounded=True):
    try:
        asset = Image.open(asset_path).convert("RGBA")
        asset = asset.resize((size, size), Image.LANCZOS)
        if rounded:
            mask = Image.new("L", (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=20, fill=255)
            base.paste(asset, (x, y), mask)
        else:
            base.paste(asset, (x, y))
    except FileNotFoundError:
        pass


def two_col_layout():
    gap = 80
    text_w = 700
    total_w = text_w + gap + IMG_SIZE
    start_x = (WIDTH - total_w) // 2
    text_x = start_x
    img_x = start_x + text_w + gap
    return text_x, img_x, CONTENT_Y + CONTENT_GAP


def two_col_layout_img_left():
    gap = 80
    text_w = 700
    total_w = IMG_SIZE + gap + text_w
    start_x = (WIDTH - total_w) // 2
    img_x = start_x
    text_x = start_x + IMG_SIZE + gap
    return img_x, text_x, CONTENT_Y + CONTENT_GAP


# ── Slides ──

def slide_title():
    img, draw = white_bg()

    # True vertical center
    block_h = 380  # total height of content block
    cy = (HEIGHT - block_h) // 2

    draw_centered(draw, "SELF INTRODUCTION", cy, get_font(32), ORANGE)
    draw_accent_line(draw, cy + 50)
    draw_centered(draw, "自己紹介", cy + 80, get_font(80, bold=True), DARK)
    draw_centered(draw, "llechi", cy + 190, get_font(60), DARK)
    draw_accent_line(draw, cy + 270)
    draw_centered(draw, "Web Engineer × AI で未来をつくる", cy + 300, get_font(40), ORANGE)

    return img


def slide_work():
    img, draw = white_bg()
    draw_title_block(draw, "WORK", "仕事について")

    text_x, img_x, y = two_col_layout()

    draw.text((text_x, y), "Webエンジニア", font=get_font(42, bold=True), fill=ORANGE)
    y += 55 + HEADING_GAP
    y = draw_wrapped(draw,
                     "Webエンジニアとして大企業で働いています。",
                     text_x, y, get_font(34), max_width=700)
    y += SECTION_GAP

    draw.text((text_x, y), "AI 活用", font=get_font(42, bold=True), fill=ORANGE)
    y += 55 + HEADING_GAP
    y = draw_wrapped(draw,
                     "建築関係の最適化の仕事を行っています。\nAIを活用した業務効率化・最適化に取り組んでいます。",
                     text_x, y, get_font(34), max_width=700)

    place_image(img, ASSETS_DIR / "work.png", img_x, CONTENT_Y + CONTENT_GAP, IMG_SIZE)

    return img


def slide_anime():
    img, draw = white_bg()
    draw_title_block(draw, "HOBBY 1", "趣味その１ ─ アニメ")

    # Wide image right below title
    banner_w = 1600
    banner_h = 280
    banner_x = (WIDTH - banner_w) // 2
    banner_y = TITLE_LINE_Y + 20
    place_image_wide(img, ASSETS_DIR / "anime2.png", banner_x, banner_y, banner_w, banner_h)

    # Text below image
    text_x = (WIDTH - 1200) // 2
    y = banner_y + banner_h + 40

    draw.text((text_x, y), "深夜アニメが大好き", font=get_font(42, bold=True), fill=ORANGE)
    y += 55 + HEADING_GAP
    y = draw_wrapped(draw,
                     "特に転生系アニメにハマっています！",
                     text_x, y, get_font(34), max_width=1200)
    y += SECTION_GAP

    draw.text((text_x, y), "お気に入り作品", font=get_font(36, bold=True), fill=ORANGE)
    y += 50 + HEADING_GAP

    favorites = [
        "転生したら剣でした",
        "転生したらスライムだった件",
        "無職転生",
        "戦姫絶唱シンフォギア",
    ]
    for fav in favorites:
        draw.text((text_x + 20, y), f"・ {fav}", font=get_font(30), fill=DARK)
        y += 46

    return img


def slide_vocaloid():
    img, draw = white_bg()
    draw_title_block(draw, "HOBBY 2", "趣味その２ ─ ボカロ")

    # Wide image right below title
    banner_w = 1600
    banner_h = 280
    banner_x = (WIDTH - banner_w) // 2
    banner_y = TITLE_LINE_Y + 20
    place_image_wide(img, ASSETS_DIR / "vocaloid2.png", banner_x, banner_y, banner_w, banner_h)

    # Text below image
    text_x = (WIDTH - 1200) // 2
    y = banner_y + banner_h + 40

    draw.text((text_x, y), "初音ミクが大好き！", font=get_font(42, bold=True), fill=ORANGE)
    y += 55 + HEADING_GAP
    y = draw_wrapped(draw,
                     "毎年ライブに参加しています。",
                     text_x, y, get_font(34), max_width=1200)
    y += SECTION_GAP

    draw.text((text_x, y), "参戦イベント", font=get_font(36, bold=True), fill=ORANGE)
    y += 50 + HEADING_GAP

    events = ["マジカルミライ（マジミラ）", "セカライ"]
    for ev in events:
        draw.text((text_x + 20, y), f"・ {ev}", font=get_font(34), fill=DARK)
        y += 50

    return img


def slide_summary():
    img, draw = white_bg()
    draw_title_block(draw, "SUMMARY", "まとめ")

    items = [
        ("Webエンジニア", "大企業でWebエンジニアとして活躍"),
        ("AI", "建築関係のAI最適化に取り組む"),
        ("アニメ", "転生系アニメ・シンフォギアが好き"),
        ("ボカロ", "初音ミク推し / マジミラ・セカライ参戦"),
        ("ゲーム・他", "スマブラ・カラオケも大好き"),
    ]

    label_font = get_font(36, bold=True)
    desc_font = get_font(30)

    # Start right after title block (same gap as slide 4)
    y = CONTENT_Y + CONTENT_GAP

    label_w = 300
    gap = 50
    total_w = label_w + gap + 700
    start_x = (WIDTH - total_w) // 2

    item_height = 65
    for label, desc in items:
        bbox = draw.textbbox((0, 0), label, font=label_font)
        lw = bbox[2] - bbox[0]
        draw.text((start_x + label_w - lw, y), label, font=label_font, fill=ORANGE)
        draw.text((start_x + label_w + gap, y + 4), desc, font=desc_font, fill=DARK)
        y += item_height

    y += 60
    draw_centered(draw, "Thank you!", y, get_font(52, bold=True), ORANGE)

    return img


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    slides = [
        ("slide_1_title.png", slide_title),
        ("slide_2_work.png", slide_work),
        ("slide_3_anime.png", slide_anime),
        ("slide_4_vocaloid.png", slide_vocaloid),
        ("slide_5_summary.png", slide_summary),
    ]

    for filename, create_fn in slides:
        img = create_fn()
        path = OUTPUT_DIR / filename
        img.save(path, "PNG")
        print(f"Created: {path}")

    print(f"\nDone! {len(slides)} slides saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
