from dataclasses import dataclass
from typing import Optional

from backend.src.domain.value_objects.slide.slide_content import SlideContent
from backend.src.domain.value_objects.slide.slide_title import SlideTitle


@dataclass(frozen=True)
class Slide:
    title: SlideTitle
    content: SlideContent
    subtitle: Optional[str] = None
    bullet_points: tuple[str, ...] = ()
    image_data: Optional[str] = None
    chart_data: Optional[dict] = None

    def has_bullet_points(self) -> bool:
        return len(self.bullet_points) > 0

    def has_chart(self) -> bool:
        return self.chart_data is not None
