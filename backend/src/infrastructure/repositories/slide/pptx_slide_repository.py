import base64
import io

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from backend.src.constants.slide import (
    ACCENT_BAR_HEIGHT_EMU,
    FONT_SIZE_BODY,
    FONT_SIZE_HEADING,
    FONT_SIZE_MAIN_TITLE,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_TITLE,
    PPTX_IMAGE_HEIGHT_INCHES,
    PPTX_IMAGE_LEFT_INCHES,
    PPTX_IMAGE_TOP_INCHES,
    PPTX_IMAGE_WIDTH_INCHES,
    PPTX_TEXT_WIDTH_DEFAULT_INCHES,
    PPTX_TEXT_WIDTH_WITH_IMAGE_INCHES,
    SLIDE_HEIGHT_INCHES,
    SLIDE_WIDTH_INCHES,
)
from backend.src.domain.commons.result import Result, failure, success
from backend.src.domain.entities.slide.slide import Slide
from backend.src.domain.entities.slide.slide_deck import SlideDeck
from backend.src.domain.repositories.slide.slide_repository import SlideRepository

ORANGE = RGBColor(240, 130, 40)
DARK = RGBColor(50, 50, 50)
WHITE = RGBColor(255, 255, 255)


class PptxSlideRepository(SlideRepository):
    def generate_pptx(self, slide_deck: SlideDeck) -> Result[bytes, Exception]:
        prs = Presentation()
        prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
        prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)

        self._add_title_slide(prs, slide_deck)

        for slide_entity in slide_deck.slides:
            self._add_content_slide(prs, slide_entity)

        buffer = io.BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        return success(buffer.getvalue())

    def _set_slide_bg(self, slide: object, color: RGBColor = WHITE) -> None:
        bg = slide.background  # type: ignore[attr-defined]
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color

    def _add_accent_bar(self, slide: object, top: bool = False, bottom: bool = False) -> None:
        bar_h = Emu(ACCENT_BAR_HEIGHT_EMU)
        slide_w = Inches(SLIDE_WIDTH_INCHES)
        slide_h = Inches(SLIDE_HEIGHT_INCHES)
        if top:
            shape = slide.shapes.add_shape(1, 0, 0, slide_w, bar_h)  # type: ignore[attr-defined]
            shape.fill.solid()
            shape.fill.fore_color.rgb = ORANGE
            shape.line.fill.background()
        if bottom:
            shape = slide.shapes.add_shape(1, 0, slide_h - bar_h, slide_w, bar_h)  # type: ignore[attr-defined]
            shape.fill.solid()
            shape.fill.fore_color.rgb = ORANGE
            shape.line.fill.background()

    def _add_text_box(
        self,
        slide: object,
        left: Emu,
        top: Emu,
        width: Emu,
        height: Emu,
        text: str,
        font_size: int = FONT_SIZE_BODY,
        bold: bool = False,
        color: RGBColor = DARK,
        alignment: PP_ALIGN = PP_ALIGN.LEFT,
    ) -> None:
        txbox = slide.shapes.add_textbox(left, top, width, height)  # type: ignore[attr-defined]
        tf = txbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.alignment = alignment

    def _add_accent_line(self, slide: object, left: Emu, top: Emu, width: Emu) -> None:
        shape = slide.shapes.add_shape(1, left, top, width, Emu(30000))  # type: ignore[attr-defined]
        shape.fill.solid()
        shape.fill.fore_color.rgb = ORANGE
        shape.line.fill.background()

    def _add_title_slide(self, prs: Presentation, slide_deck: SlideDeck) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._set_slide_bg(slide)
        self._add_accent_bar(slide, top=True, bottom=True)

        slide_w = Inches(SLIDE_WIDTH_INCHES)

        self._add_text_box(
            slide, Inches(0), Inches(2.0), slide_w, Inches(0.5),
            slide_deck.title.value, FONT_SIZE_MAIN_TITLE, True, DARK, PP_ALIGN.CENTER,
        )

        self._add_accent_line(slide, Inches(4.5), Inches(3.0), Inches(4.3))

        if slide_deck.author:
            self._add_text_box(
                slide, Inches(0), Inches(3.3), slide_w, Inches(0.5),
                slide_deck.author, FONT_SIZE_TITLE, False, DARK, PP_ALIGN.CENTER,
            )

    def _add_image_to_slide(self, slide: object, image_data: str) -> None:
        raw = base64.b64decode(image_data)
        image_stream = io.BytesIO(raw)
        slide.shapes.add_picture(  # type: ignore[attr-defined]
            image_stream,
            Inches(PPTX_IMAGE_LEFT_INCHES),
            Inches(PPTX_IMAGE_TOP_INCHES),
            Inches(PPTX_IMAGE_WIDTH_INCHES),
            Inches(PPTX_IMAGE_HEIGHT_INCHES),
        )

    def _add_slide_header(self, slide: object, slide_entity: Slide) -> None:
        slide_w = Inches(SLIDE_WIDTH_INCHES)
        if slide_entity.subtitle:
            self._add_text_box(
                slide, Inches(0), Inches(0.4), slide_w, Inches(0.4),
                slide_entity.subtitle, FONT_SIZE_SUBTITLE, False, ORANGE, PP_ALIGN.CENTER,
            )
        self._add_text_box(
            slide, Inches(0), Inches(0.8), slide_w, Inches(0.7),
            slide_entity.title.value, FONT_SIZE_TITLE, True, DARK, PP_ALIGN.CENTER,
        )
        self._add_accent_line(slide, Inches(4.5), Inches(1.5), Inches(4.3))

    def _add_slide_body(self, slide: object, slide_entity: Slide, text_w: Emu) -> None:
        content_y = Inches(2.0)
        if slide_entity.content.value:
            self._add_text_box(
                slide, Inches(1.2), content_y, text_w, Inches(2.0),
                slide_entity.content.value, FONT_SIZE_BODY, False, DARK,
            )
            content_y = Inches(3.5)
        if slide_entity.has_bullet_points():
            for i, point in enumerate(slide_entity.bullet_points):
                y = content_y + Inches(i * 0.45)
                self._add_text_box(
                    slide, Inches(1.5), y, text_w, Inches(0.4),
                    f"  {point}", FONT_SIZE_BODY, False, DARK,
                )

    def _add_content_slide(self, prs: Presentation, slide_entity: Slide) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._set_slide_bg(slide)
        self._add_accent_bar(slide, top=True, bottom=True)

        has_image = bool(slide_entity.image_data)
        text_w = Inches(PPTX_TEXT_WIDTH_WITH_IMAGE_INCHES) if has_image else Inches(PPTX_TEXT_WIDTH_DEFAULT_INCHES)

        self._add_slide_header(slide, slide_entity)
        self._add_slide_body(slide, slide_entity, text_w)

        if has_image and slide_entity.image_data:
            self._add_image_to_slide(slide, slide_entity.image_data)
