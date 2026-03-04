# AI Slide Generator

テーマを入力するだけで、AIがスライド構成・イラストを自動生成し、PowerPoint ファイルとしてダウンロードできる Web アプリケーション。

## 機能

- テーマとスライド枚数を指定するだけで、AI がスライド構成を自動生成
- 各スライドに AI イラスト（Imagen 4）を自動挿入
- プレビュー画面でスライドの内容を確認
- 修正指示を入力して何度でも内容を改善（AI と往復）
- 満足したら PowerPoint (.pptx) としてダウンロード

## デモ

```
1. テーマ入力 → 2. AI が生成 → 3. プレビュー確認 → 4. 修正指示 → 5. ダウンロード
```

### ユーザーフロー

1. テーマ（例: 「AI の未来と社会への影響」）とスライド枚数を入力
2. AI がスライド構成（タイトル・本文・箇条書き）+ イラストを生成
3. プレビュー画面で生成されたスライド画像を確認
4. 修正が必要なら指示を入力（例: 「3枚目にデータの具体例を追加して」）→ AI が再生成
5. 満足したら「ダウンロード」ボタンで .pptx ファイルを取得

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| Backend | Python 3.12 / FastAPI / Uvicorn |
| Frontend | React 19 / TypeScript / Tailwind CSS / Vite |
| AI (テキスト) | Google Gemini API (`gemini-2.5-flash`) |
| AI (画像) | Google Imagen API (`imagen-4.0-generate-001`) |
| スライド生成 | python-pptx（PPTX） / Pillow（プレビュー画像） |
| インフラ | Docker / Docker Compose / AWS CDK（Lambda + CloudFront） |
| テスト | pytest / Playwright / httpx |

## アーキテクチャ

DDD + クリーンアーキテクチャ。詳細は [docs/architecture.md](docs/architecture.md) を参照。

```
Presentation (FastAPI Routes / Controllers)
    ↓
Application (UseCases / DTOs / Services)
    ↓
Domain (Entities / Value Objects / Repository Interfaces)
    ↑
Infrastructure (Gemini Client / PPTX Generator / PIL Renderer)
```

## セットアップ

### 前提条件

- Docker / Docker Compose
- Google Cloud の API キー（Gemini API + Imagen API 有効化済み）

### 手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/LlechiKaito/ai-create-slide.git
cd ai-create-slide

# 2. 環境変数を設定
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定

# 3. 起動
docker compose up -d

# 4. ブラウザでアクセス
open http://localhost
```

### 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `GEMINI_API_KEY` | Yes | Google Gemini API キー |
| `CORS_ALLOWED_ORIGINS` | No | CORS 許可オリジン（デフォルト: `http://localhost:5173`） |
| `HOST` | No | バックエンドホスト（デフォルト: `0.0.0.0`） |
| `PORT` | No | バックエンドポート（デフォルト: `8000`） |

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/health` | ヘルスチェック |
| POST | `/api/slides/ai-generate` | テーマからスライドを AI 生成 |
| POST | `/api/slides/ai-revise` | 生成済みスライドを修正指示で改善 |
| POST | `/api/slides/preview-images` | スライドのプレビュー画像を生成 |
| POST | `/api/slides/generate` | スライドデータから PPTX をダウンロード |

## テスト

```bash
# ユニット + インテグレーションテスト
python3 -m pytest tests/unit/ tests/integration/ -v

# E2E テスト（Docker 環境が起動している状態で）
docker compose up -d
npx playwright test
docker compose down
```

| テスト種別 | 件数 | 場所 |
|-----------|------|------|
| ユニット | 28 | `tests/unit/` |
| インテグレーション | 14 | `tests/integration/` |
| E2E (Playwright) | 9 | `tests/e2e/` |

## プロジェクト構成

```
ai-create-slide/
├── backend/                 ← FastAPI バックエンド
│   └── src/
│       ├── domain/          ← エンティティ・値オブジェクト・リポジトリIF
│       ├── application/     ← ユースケース・DTO・サービス
│       ├── infrastructure/  ← Gemini クライアント・PPTX/PIL 実装
│       ├── presentation/    ← ルート・コントローラー・エラーハンドラ
│       ├── container/       ← DI コンテナ
│       └── constants/       ← 定数
├── frontend/                ← React フロントエンド
│   └── src/
│       ├── pages/           ← ページコンポーネント
│       ├── components/      ← UI コンポーネント
│       ├── hooks/           ← ロジック（カスタムフック）
│       ├── services/        ← API クライアント（axios）
│       ├── types/           ← TypeScript 型定義
│       └── constants/       ← 定数
├── infra/                   ← AWS CDK（Lambda + CloudFront）
├── tests/                   ← テストスイート
│   ├── unit/                ← ユニットテスト
│   ├── integration/         ← インテグレーションテスト
│   └── e2e/                 ← E2E テスト（Playwright）
└── docker-compose.yml
```

## AWS デプロイ手順

### 前提条件

- AWS CLI 設定済み（`aws configure`）
- AWS CDK Toolkit インストール済み（`npm install -g aws-cdk`）
- CDK Bootstrap 実行済み（`cdk bootstrap aws://ACCOUNT_ID/REGION`）
- Docker（CDK がコンテナイメージをビルドするため）

### インフラ構成

| スタック | リソース | 説明 |
|---------|---------|------|
| `SlideGen-{env}-Api` | Lambda (Docker) + Function URL | バックエンド API |
| `SlideGen-{env}-Frontend` | S3 + CloudFront | フロントエンド配信 |

### デプロイ手順

```bash
# 1. GEMINI_API_KEY を SSM Parameter Store に登録
aws ssm put-parameter --name "/slide-gen/dev/gemini-api-key" --type SecureString --value "your-gemini-api-key" --region ap-northeast-1

# 2. CDK の依存をインストール
cd infra
npm install

# 3. バックエンドをデプロイ（Lambda Function URL を取得）
npx cdk deploy SlideGen-dev-Api --context env=dev

# 4. 出力された BackendUrl を確認し、フロントエンドをビルド
cd ../frontend
VITE_API_URL=https://xxxxxxxxxx.lambda-url.ap-northeast-1.on.aws npm run build

# 5. フロントエンドをデプロイ
cd ../infra
npx cdk deploy SlideGen-dev-Frontend --context env=dev
```

### 環境別デプロイ

```bash
# dev 環境（Lambda 512MB）
npx cdk deploy --all --context env=dev

# prod 環境（Lambda 1024MB）
npx cdk deploy --all --context env=prod
```

### GEMINI_API_KEY の設定（SSM Parameter Store）

デプロイ前に SSM Parameter Store に API キーを登録してください。

```bash
# dev 環境
aws ssm put-parameter --name "/slide-gen/dev/gemini-api-key" --type SecureString --value "your-gemini-api-key" --region ap-northeast-1

# prod 環境
aws ssm put-parameter --name "/slide-gen/prod/gemini-api-key" --type SecureString --value "your-gemini-api-key" --region ap-northeast-1
```

Lambda は起動時に SSM から自動取得します。

### リソース削除

```bash
npx cdk destroy --all --context env=dev
```

## CLI ツール（オプション）

既存の CLI ツールは `profiles: ["cli"]` で分離済み。手動実行する場合:

```bash
# 画像生成
docker compose run --rm generate "A robot holding a red skateboard"

# スライド画像生成
docker compose run --rm slides

# PPTX 生成
docker compose run --rm pptx
```
