import json
import os

from google import genai
from google.genai import types

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.constants.slide import GEMINI_MODEL_NAME, IMAGEN_MODEL_NAME
from backend.src.domain.commons.result import Result, failure, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository

SYSTEM_PROMPT = """あなたはプレゼンテーション作成のプロです。
ユーザーのテーマに基づいて、スライドの構成を JSON で出力してください。

出力形式（厳守）:
{
  "deck_title": "プレゼンテーションのタイトル",
  "author": "",
  "slides": [
    {
      "title": "スライドタイトル",
      "subtitle": "サブタイトル（任意）",
      "content": "本文テキスト（任意）",
      "bullet_points": ["箇条書き1", "箇条書き2"],
      "image_prompt": "English description of an illustration for this slide"
    }
  ]
}

ルール:
- JSON のみ出力。説明文やマークダウンは不要
- 各スライドには必ず title を入れる
- content と bullet_points は両方あってもよいし、片方だけでもよい
- 各スライドに image_prompt を入れる（英語で、そのスライドの内容を表すイラストの説明）
- image_prompt はシンプルで具体的に書く（例: "A robot arm assembling a car in a factory"）
- 日本語で出力する（image_prompt のみ英語）
- スライドは指定された枚数で作成する
"""

REVISE_PROMPT = """あなたはプレゼンテーション作成のプロです。
現在のスライド内容と修正指示を受け取り、修正後のスライド構成を JSON で出力してください。

出力形式（厳守）:
{
  "deck_title": "プレゼンテーションのタイトル",
  "author": "",
  "slides": [
    {
      "title": "スライドタイトル",
      "subtitle": "サブタイトル（任意）",
      "content": "本文テキスト（任意）",
      "bullet_points": ["箇条書き1", "箇条書き2"],
      "image_prompt": "English description of an illustration for this slide"
    }
  ]
}

ルール:
- JSON のみ出力。説明文やマークダウンは不要
- 修正指示に従って内容を変更する
- 指示されていない部分はそのまま維持する
- 各スライドに image_prompt を入れる（英語で、そのスライドの内容を表すイラストの説明）
- 日本語で出力する（image_prompt のみ英語）
"""


class GeminiAiSlideRepository(AiSlideRepository):
    def _get_client(self) -> genai.Client:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ApplicationError(**APPLICATION_ERRORS["GEMINI_API_KEY_NOT_SET"])
        return genai.Client(api_key=api_key)

    def _parse_json_response(self, text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)

    def generate_slide_content(
        self, theme: str, num_slides: int
    ) -> Result[dict, Exception]:
        client = self._get_client()

        user_message = f"テーマ: {theme}\nスライド枚数: {num_slides}枚"

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_message}]},
            ],
        )

        parsed = self._parse_json_response(response.text)
        return success(parsed)

    def revise_slide_content(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        client = self._get_client()

        current_json = json.dumps(current_content, ensure_ascii=False, indent=2)
        user_message = (
            f"現在のスライド内容:\n{current_json}\n\n"
            f"修正指示: {revision_instruction}"
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": REVISE_PROMPT + "\n\n" + user_message}]},
            ],
        )

        parsed = self._parse_json_response(response.text)
        return success(parsed)

    def generate_image(self, prompt: str) -> Result[bytes, Exception]:
        try:
            client = self._get_client()
            response = client.models.generate_images(
                model=IMAGEN_MODEL_NAME,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    safety_filter_level="BLOCK_ONLY_HIGH",
                ),
            )
        except Exception as e:
            return failure(e)

        if not response.generated_images:
            return failure(Exception("No image generated"))

        return success(response.generated_images[0].image.image_bytes)
