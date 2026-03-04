# アーキテクチャドキュメント

## 概要

AI Slide Generator は、DDD（ドメイン駆動設計）+ クリーンアーキテクチャの思想に基づいた Web アプリケーション。テーマを入力するだけで、AI がスライド構成とイラストを自動生成し、PowerPoint ファイルとしてダウンロードできる。

## システム構成図

```
┌─────────────┐      ┌──────────────────────────────────────┐
│   Browser    │ ───→ │  Frontend (React + Nginx)  :80      │
│             │ ←─── │    ├── /           → SPA             │
│             │      │    └── /api/*      → proxy to :8000  │
└─────────────┘      └──────────────┬───────────────────────┘
                                    │
                                    ↓
                     ┌──────────────────────────────────────┐
                     │  Backend (FastAPI + Uvicorn)  :8000  │
                     │    ├── POST /api/slides/ai-generate  │
                     │    ├── POST /api/slides/ai-revise    │
                     │    ├── POST /api/slides/preview-images│
                     │    └── POST /api/slides/generate     │
                     └─────┬──────────────┬─────────────────┘
                           │              │
                    ┌──────┘              └──────┐
                    ↓                            ↓
          ┌─────────────────┐          ┌─────────────────┐
          │  Gemini API     │          │  Imagen API     │
          │  (テキスト生成)  │          │  (画像生成)     │
          │  gemini-2.5-flash│         │  imagen-4.0     │
          └─────────────────┘          └─────────────────┘
```

## レイヤー構成

```
backend/src/
├── presentation/    ← HTTP の入出口。ビジネスロジックを書かない
│   ├── routes/      ← FastAPI ルート定義
│   ├── controllers/ ← リクエスト→サービス→レスポンス変換
│   └── errors/      ← エラーハンドラ（AOP: 横断的関心事）
│
├── application/     ← ユースケースの実現。domain にのみ依存
│   ├── usecases/    ← 1ユースケース = 1ビジネスフロー
│   ├── services/    ← ユースケースのオーケストレーター
│   ├── dto/         ← リクエスト/レスポンスの型定義（Pydantic）
│   └── errors/      ← アプリケーションエラー定義
│
├── domain/          ← ビジネスの核。外部技術に一切依存しない
│   ├── entities/    ← Slide, SlideDeck
│   ├── value_objects/← SlideTitle, SlideContent
│   ├── repositories/← インターフェースのみ（実装は infrastructure）
│   ├── commons/     ← Result 型（Success / Failure）
│   └── errors/      ← ドメインエラー定義
│
├── infrastructure/  ← 外部技術の実装。domain のインターフェースを実装
│   ├── external/    ← Gemini API クライアント
│   └── repositories/← PPTX 生成、PIL プレビュー描画
│
├── container/       ← DI コンテナ（依存の組み立て）
├── constants/       ← マジックナンバー・定数の一元管理
└── config/          ← 環境変数の読み込み
```

### 依存方向

```
Presentation → Application → Domain ← Infrastructure
```

- **Domain** は外側を知らない（最も安定したレイヤー）
- **Application** は Domain にのみ依存
- **Infrastructure** は Domain のインターフェースを実装
- **Presentation** は Application を呼び出す
- **Container** が全レイヤーを組み立てる（DI）

## ユースケース一覧

| ユースケース | 入力 | 出力 | 説明 |
|-------------|------|------|------|
| `AiGenerateUseCase` | テーマ, 枚数 | スライド構成 + 画像 | Gemini でテキスト生成 → Imagen で画像生成 |
| `AiReviseUseCase` | 現在の構成, 修正指示 | 修正済み構成 + 画像 | Gemini で修正 → Imagen で画像再生成 |
| `PreviewImagesUseCase` | スライドデータ | PNG 画像リスト | PIL でスライドをレンダリング |
| `GenerateSlideUseCase` | スライドデータ | PPTX バイナリ | python-pptx で PowerPoint 生成 |

## データフロー

### AI 生成フロー

```
ユーザー入力 (テーマ: "AIの未来", 枚数: 5)
    ↓
AiGenerateUseCase
    ├── Gemini API → JSON (deck_title, slides[{title, content, bullet_points, image_prompt}])
    └── Imagen API → 各スライドの image_prompt から画像生成 (base64)
    ↓
フロントエンドに返却 (AiGenerateResponse)
    ↓
PreviewImagesUseCase
    └── PIL でスライド画像をレンダリング (1920x1080 PNG)
    ↓
ブラウザでプレビュー表示
```

### 修正フロー

```
ユーザー修正指示 ("3枚目にデータの具体例を追加して")
    ↓
AiReviseUseCase
    ├── Gemini API → 現在の構成 + 修正指示 → 修正済み JSON
    └── Imagen API → 画像再生成
    ↓
プレビュー更新
```

### ダウンロードフロー

```
ダウンロードボタン押下
    ↓
GenerateSlideUseCase
    └── python-pptx で PPTX 生成
        ├── タイトルスライド（デッキタイトル + 著者）
        └── コンテンツスライド × N
            ├── テキスト（タイトル・本文・箇条書き）
            └── 画像（image_data があれば右側に配置）
    ↓
ブラウザでファイルダウンロード (.pptx)
```

## ドメインモデル

### Entity

```python
@dataclass(frozen=True)
class Slide:
    title: SlideTitle          # 必須
    content: SlideContent      # 任意（空文字可）
    subtitle: Optional[str]    # 任意
    bullet_points: tuple[str, ...]  # 0個以上
    image_data: Optional[str]  # base64 エンコード画像（任意）

@dataclass(frozen=True)
class SlideDeck:
    title: SlideTitle          # デッキタイトル
    slides: tuple[Slide, ...]  # 1〜20枚
    author: str                # 著者（任意）
```

### Value Object

```python
@dataclass(frozen=True)
class SlideTitle:
    value: str  # 1〜200文字、空白のみ不可

@dataclass(frozen=True)
class SlideContent:
    value: str  # 0〜5000文字
```

### Repository Interface

```python
class AiSlideRepository(ABC):
    def generate_slide_content(theme, num_slides) -> Result[dict, Exception]
    def revise_slide_content(current_content, revision_instruction) -> Result[dict, Exception]
    def generate_image(prompt) -> Result[bytes, Exception]

class SlideRepository(ABC):
    def generate_pptx(slide_deck) -> Result[bytes, Exception]

class SlidePreviewRepository(ABC):
    def render_preview_images(deck_title, author, slides) -> Result[list[bytes], Exception]
```

## エラーハンドリング

### Result 型

```python
Result = Union[Success[T], Failure[E]]

# 成功
success(data) → Success(data=data, is_success=True)

# 失敗
failure(error) → Failure(error=error, is_success=False)
```

### エラーハンドラ（AOP）

Presentation 層でのみ例外をキャッチ。ミドルウェアとして登録:

| ハンドラ | 対象 | HTTP ステータス |
|---------|------|----------------|
| `domain_error_handler` | `DomainError` | 400 |
| `application_error_handler` | `ApplicationError` | エラーごとに定義 |
| `generic_error_handler` | `Exception` | 500 |

### 画像生成の失敗耐性

画像生成（Imagen API）が失敗しても、スライド生成全体は中断しない:

```
generate_image() → 成功: base64 画像 → スライドに埋め込み
                 → 失敗: image_data = "" → 画像なしで続行
```

## フロントエンド構成

```
frontend/src/
├── App.tsx              ← BrowserRouter + Routes のみ
├── pages/
│   ├── slide-generator-page.tsx  ← メインページ
│   └── not-found-page.tsx        ← 404 ページ
├── components/ai-slide/
│   ├── theme-input-form.tsx      ← テーマ入力フォーム
│   ├── slide-preview.tsx         ← スライドプレビュー表示
│   └── revision-form.tsx         ← 修正指示 + ダウンロード + リセット
├── hooks/
│   └── use-ai-slide-generator.ts ← 全ロジック集約
├── services/
│   ├── api-client.ts             ← axios ベースクライアント
│   └── slide-service.ts          ← API エンドポイント定義
├── types/
│   └── slide.ts                  ← TypeScript 型定義
└── constants/
    ├── api.ts                    ← API パス
    ├── config.ts                 ← 環境変数
    ├── errors.ts                 ← エラーメッセージ
    └── slide.ts                  ← スライド関連定数
```

### ステップ遷移

```
"input" ステップ              "preview" ステップ
┌─────────────────┐          ┌─────────────────────────┐
│ ThemeInputForm   │  生成→   │ SlidePreview            │
│ - テーマ入力     │          │ - プレビュー画像表示    │
│ - 枚数指定       │          │                         │
│ - 生成ボタン     │          │ RevisionForm            │
└─────────────────┘  ←リセット │ - 修正指示入力          │
                              │ - ダウンロードボタン    │
                              │ - リセットボタン        │
                              └─────────────────────────┘
```

## インフラ構成（AWS CDK）

```
┌─────────────────────────────────────────┐
│  VPC                                     │
│  ┌─────────────────────────────────────┐ │
│  │  ECS Cluster                        │ │
│  │  ┌─────────────────────────────────┐│ │
│  │  │  Fargate Service               ││ │
│  │  │  ┌──────────┐  ┌────────────┐ ││ │
│  │  │  │ Backend  │  │ Frontend   │ ││ │
│  │  │  │ :8000    │  │ :80        │ ││ │
│  │  │  └──────────┘  └────────────┘ ││ │
│  │  └─────────────────────────────────┘│ │
│  └─────────────────────────────────────┘ │
│  ┌──────────────┐                        │
│  │  ALB         │ ← インターネットからのアクセス │
│  └──────────────┘                        │
└─────────────────────────────────────────┘
```

| 環境 | CPU | メモリ | インスタンス数 |
|------|-----|--------|--------------|
| dev | 256 | 512 MB | 1 |
| prod | 512 | 1024 MB | 2 |

## スライドデザイン

### カラースキーム

| 用途 | 色 | RGB |
|------|----|----|
| アクセント | オレンジ | (240, 130, 40) |
| テキスト | ダークグレー | (50, 50, 50) |
| 背景 | 白 | (255, 255, 255) |
| サブテキスト | ライトグレー | (180, 180, 180) |

### スライドレイアウト

**タイトルスライド:**
```
┌──────────────────────────────┐
│████████████████████████████████│ ← オレンジアクセントバー
│                                │
│         ─────────              │ ← オレンジライン
│       デッキタイトル           │ ← 太字 48pt
│         著者名                 │ ← 36pt
│         ─────────              │ ← オレンジライン
│                                │
│████████████████████████████████│ ← オレンジアクセントバー
└──────────────────────────────┘
```

**コンテンツスライド（画像あり）:**
```
┌──────────────────────────────┐
│████████████████████████████████│
│ サブタイトル                   │
│ スライドタイトル               │
│ ─────────                      │
│ 本文テキスト     ┌──────────┐ │
│ ● 箇条書き1      │          │ │
│ ● 箇条書き2      │  画像    │ │
│ ● 箇条書き3      │          │ │
│                   └──────────┘ │
│████████████████████████████████│
└──────────────────────────────┘
```

## テスト戦略

| 種別 | 件数 | フレームワーク | 対象 |
|------|------|---------------|------|
| ユニット | 28 | pytest | エンティティ、ユースケース |
| インテグレーション | 14 | pytest + httpx | API エンドポイント |
| E2E | 9 | Playwright | ユーザーフロー全体 |

### テスト対象

- **ユニット**: SlideTitle/SlideContent バリデーション、Slide/SlideDeck 生成、AI 生成/修正ユースケース、プレビュー画像ユースケース
- **インテグレーション**: 全 API エンドポイント、バリデーションエラー（422）、AI 生成成功パス
- **E2E**: ページ表示、テーマ入力バリデーション、AI 生成→プレビュー表示、修正指示バリデーション、リセット、404 ページ
