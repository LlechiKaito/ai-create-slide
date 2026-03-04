MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 5000
MAX_SLIDES_PER_DECK = 20
MAX_BULLET_POINTS_PER_SLIDE = 10

SLIDE_WIDTH_INCHES = 13.333
SLIDE_HEIGHT_INCHES = 7.5

ACCENT_BAR_HEIGHT_EMU = 80000

FONT_NAME_DEFAULT = ""

PPTX_FONT_SIZE_TITLE = {"small": 26, "medium": 32, "large": 38}
PPTX_FONT_SIZE_BODY = {"small": 18, "medium": 22, "large": 26}
PPTX_FONT_SIZE_ACCENT = {"small": 16, "medium": 20, "large": 24}
DEFAULT_FONT_SIZE_LEVEL = "medium"

PREVIEW_FONT_SIZE_TITLE = {"small": 38, "medium": 48, "large": 56}
PREVIEW_FONT_SIZE_BODY = {"small": 22, "medium": 28, "large": 34}
PREVIEW_FONT_SIZE_ACCENT = {"small": 22, "medium": 28, "large": 34}

GENERATED_FILENAME = "generated_slides.pptx"

PPTX_IMAGE_SIZES = {
    "small": {"width": 3.5, "height": 3.0},
    "medium": {"width": 5.0, "height": 4.5},
    "large": {"width": 6.5, "height": 5.5},
}
DEFAULT_IMAGE_SIZE = "medium"

PPTX_CONTENT_GAPS = {
    "narrow": 0.3,
    "medium": 0.5,
    "wide": 1.0,
}
DEFAULT_CONTENT_GAP = "medium"

PPTX_IMAGE_RIGHT_MARGIN = 0.8
PPTX_TEXT_WIDTH_WITH_CHART_INCHES = 6.0
PPTX_TEXT_WIDTH_DEFAULT_INCHES = 11.0

PREVIEW_IMAGE_SIZES = {
    "small": 360,
    "medium": 520,
    "large": 680,
}
PREVIEW_CONTENT_GAPS = {
    "narrow": 20,
    "medium": 40,
    "wide": 80,
}

PPTX_CHART_WIDTH_INCHES = 5.5
PPTX_CHART_HEIGHT_INCHES = 4.0
PPTX_CHART_LEFT_INCHES = 7.0
PPTX_CHART_TOP_INCHES = 2.0

SUPPORTED_CHART_TYPES = ("column", "bar", "line", "pie")
DIAGRAM_TYPES = ("timeline", "process", "cycle", "pyramid", "funnel", "comparison")


FONT_FAMILIES = ("gothic", "mincho")
DEFAULT_FONT_FAMILY = "gothic"
PPTX_FONT_MAP = {
    "gothic": "",
    "mincho": "Noto Serif CJK JP",
}
PIL_FONT_MAP = {
    "gothic": {
        "bold": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "regular": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    },
    "mincho": {
        "bold": "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
        "regular": "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    },
}

GEMINI_MODEL_NAME = "gemini-2.5-flash"
IMAGEN_MODEL_NAME = "imagen-4.0-generate-001"

SLIDE_CATEGORIES = {
    "sales_proposal": "営業提案書",
    "business_plan": "事業企画書",
    "training": "研修資料",
    "report": "報告書",
    "other": "その他",
}
DEFAULT_CATEGORY = "sales_proposal"

PREVIEW_WIDTH = 1920
PREVIEW_HEIGHT = 1080
PREVIEW_ACCENT_BAR = 6
PREVIEW_MARGIN_X = 120
PREVIEW_BULLET_INDENT = 40
PREVIEW_LINE_SPACING = 14
PREVIEW_ACCENT_LINE_W = 500
PREVIEW_TITLE_BLOCK_H = 300
PREVIEW_CONTENT_START_Y = 80
PREVIEW_MAX_TEXT_WIDTH = 1680

PREVIEW_FONT_PAGE_NUM = 24
