import json
import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.constants.slide import GEMINI_MODEL_NAME, IMAGEN_MODEL_NAME
from backend.src.domain.commons.result import Result, failure, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository

SYSTEM_PROMPT = """あなたは世界トップクラスのプレゼンテーションデザイナーです。
ユーザーのテーマに基づいて、プロフェッショナルなスライド構成を JSON で出力してください。

## 出力形式（厳守）
{
  "deck_title": "短く印象的なタイトル（15文字以内）",
  "author": "",
  "slides": [
    {
      "title": "スライドタイトル（20文字以内）",
      "subtitle": "サブタイトル（25文字以内、任意）",
      "content": "補足テキスト（50文字以内、任意）",
      "bullet_points": ["箇条書き（各20文字以内）"],
      "image_prompt": "English image generation prompt"
    }
  ]
}

## スライド設計原則
- 1スライド = 1メッセージ。複数の話題を詰め込まない
- 3秒で伝わるスライドを作れ（Nancy Duarte のビルボードテスト）
- テキストは最小限。聴衆が読むのではなく、発表者の話を補強する役割
- スライド全体で起承転結のストーリーを構成する

## テキストルール（厳守）
- title: 20文字以内。短く力強いメッセージ
- subtitle: 25文字以内。title の補足（なくてもよい）
- content: 50文字以内の短い補足文。長文は禁止。なくてもよい
- bullet_points: 3〜5個まで。各項目20文字以内。体言止めか短い文で統一
- content と bullet_points を両方使う場合、content は1文のみ
- 1スライドの総文字数は title 含めて100文字以内を目安にする

## スライド構成（厳守）
- 指定された枚数で作成する
- 最初のスライドは導入（テーマの提示、聴衆の関心を引く問いかけ）
- 中盤は核心（事実・データ・具体例をシンプルに提示）
- 最後のスライドは必ず「まとめ」スライドにする
  - title に「まとめ」を含める（例: "まとめ：今日のポイント"）
  - bullet_points でプレゼン全体の要点を3〜4個で簡潔に整理する
  - content で次のアクションや聴衆へのメッセージを一言添える

## image_prompt ルール（英語で記述・厳守）
全スライドで統一感のあるイラストを生成するため、以下の形式で書くこと:

形式: "A flat vector illustration of [具体的な主題], [詳細], clean lines, geometric shapes, blue and orange color palette, white background, no text, no people faces, minimalist, professional"

ルール:
- 必ず "flat vector illustration" スタイルで統一する
- カラーパレットは "blue and orange" で全スライド統一する
- 必ず "white background, no text, no people faces" を含める
- 主題はそのスライドの内容を象徴する具体的なオブジェクトやシーンにする
- 抽象的すぎる表現は避け、描画可能な具体物で表現する

## その他
- JSON のみ出力。説明文やマークダウンは不要
- 日本語で出力する（image_prompt のみ英語）
"""

REVISE_PROMPT = """あなたは世界トップクラスのプレゼンテーションデザイナーです。
現在のスライド内容と修正指示を受け取り、修正後のスライド構成を JSON で出力してください。

## 出力形式（厳守）
{
  "deck_title": "短く印象的なタイトル（15文字以内）",
  "author": "",
  "slides": [
    {
      "title": "スライドタイトル（20文字以内）",
      "subtitle": "サブタイトル（25文字以内、任意）",
      "content": "補足テキスト（50文字以内、任意）",
      "bullet_points": ["箇条書き（各20文字以内）"],
      "image_prompt": "English image generation prompt"
    }
  ]
}

## テキストルール（厳守）
- title: 20文字以内。短く力強いメッセージ
- subtitle: 25文字以内（なくてもよい）
- content: 50文字以内の短い補足文（なくてもよい）
- bullet_points: 3〜5個まで。各項目20文字以内
- 1スライド = 1メッセージ。詰め込まない

## image_prompt ルール（英語で記述・厳守）
形式: "A flat vector illustration of [具体的な主題], [詳細], clean lines, geometric shapes, blue and orange color palette, white background, no text, no people faces, minimalist, professional"
- 必ず "flat vector illustration" スタイルで統一
- カラーパレットは "blue and orange" で全スライド統一
- 必ず "white background, no text, no people faces" を含める

## その他
- JSON のみ出力。説明文やマークダウンは不要
- 修正指示に従って内容を変更する
- 指示されていない部分はそのまま維持する
- 日本語で出力する（image_prompt のみ英語）
"""


class GeminiAiSlideRepository(AiSlideRepository):
    def _get_client(self) -> genai.Client:
        from backend.src.config.settings import get_gemini_api_key

        api_key = get_gemini_api_key()
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
        logger.info("Imagen API call start: model=%s, prompt=%s", IMAGEN_MODEL_NAME, prompt[:80])
        try:
            client = self._get_client()
            response = client.models.generate_images(
                model=IMAGEN_MODEL_NAME,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                ),
            )
        except Exception as e:
            logger.error("Imagen API exception: %s: %s", type(e).__name__, e)
            return failure(e)

        if not response.generated_images:
            logger.warning("Imagen API returned no images for prompt: %s", prompt[:80])
            return failure(Exception("No image generated"))

        image_bytes = response.generated_images[0].image.image_bytes
        logger.info("Imagen API success: %d bytes", len(image_bytes))
        return success(image_bytes)
