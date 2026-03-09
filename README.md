# 二次元気分尺度 モニタリング（Streamlit MVP）

iPhone Safariでも使いやすい、二次元気分尺度の記録アプリです。

- 8項目に0〜5で回答
- 回答直後にV / S / P / Aを採点
- こころのダイアグラム（菱形）を表示
- 自由記述を保存
- 履歴（直近20件）と時系列グラフを表示
- CSVダウンロード対応
- 回答送信後、LINEへダイアグラム画像＋レポートを自動送信（設定済み時）

## 技術スタック

- Python
- Streamlit (multipage app)
- Plotly
- SQLite
- pandas
- requests
- cloudinary
- kaleido

## ファイル構成

```text
.
├── app.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── README.md
├── data/
│   └── mood_app.db  # 初回起動時に自動作成
├── utils/
│   ├── db.py
│   ├── diagram.py
│   ├── image_hosting.py
│   ├── line_messaging.py
│   ├── navigation.py
│   └── scoring.py
└── pages/
    ├── 1_回答_自分用.py
    ├── 2_回答_友人用.py
    ├── 3_履歴_自分用.py
    └── 4_履歴_友人用.py
```

## セットアップ手順

### 1) 仮想環境を作成

```bash
python -m venv .venv
```

### 2) 仮想環境を有効化

- macOS / Linux

```bash
source .venv/bin/activate
```

- Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### 3) 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4) アプリを起動

```bash
streamlit run app.py
```

## DBファイルの場所

- `data/mood_app.db`

初回起動時にテーブル `responses` を自動作成します。

## ページ構成

サイドバーから以下へ移動できます。

- 回答（秋山用）: `user_type = "self"` として保存
- 回答（明石用）: `user_type = "friend"` として保存
- 履歴（秋山用）: 秋山用データのみ表示
- 履歴（明石用）: 明石用データのみ表示

## LINE自動送信の概要

回答ページで保存した直後に、以下をLINE Messaging APIのPush Messageで送信します。

1. ダイアグラム画像（Cloudinaryへアップロード後のHTTPS URL）
2. テキストレポート

Cloudinaryアップロードが失敗した場合は、画像送信をスキップしてテキストのみ送信します。

## LINE Developers 側の設定手順

1. [LINE Developers Console](https://developers.line.biz/) でProviderを作成
2. Messaging APIチャネルを作成
3. チャネル設定でPush messageを有効化
4. Channel access token（長期）を発行
5. 自分と友人でBotを友だち追加

### LINE_USER_ID の取得（Webhook.site を使う簡易手順）

1. https://webhook.site を開き、一時URLを取得
2. LINE DevelopersのWebhook URLを一時URLに設定し、Webhookを有効化
3. Botにメッセージを送る
4. webhook.siteに届いたJSONから `source.userId` を確認
5. 自分のIDを `LINE_USER_ID_SELF`、友人のIDを `LINE_USER_ID_FRIEND` として保存
6. 取得後はWebhook URLを本来のものへ戻す（または無効化）

## Cloudinary設定手順

1. https://cloudinary.com/ でアカウント作成
2. Dashboardから以下を取得
   - `cloud_name`
   - `api_key`
   - `api_secret`
3. Streamlit secretsへ設定

## Streamlit secrets 設定

### 1) ローカル（`.streamlit/secrets.toml`）

```toml
LINE_CHANNEL_ACCESS_TOKEN="xxxxxxxxxxxxxxxx"
LINE_USER_ID_SELF="Uxxxxxxxxxxxxxxxx"
LINE_USER_ID_FRIEND="Uyyyyyyyyyyyyyyyy"

CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="your-api-key"
CLOUDINARY_API_SECRET="your-api-secret"
```

### 2) Streamlit Community Cloud

1. 対象アプリを開く
2. `Settings` → `Secrets`
3. 上記と同じキーを貼り付けて `Save`
4. `Reboot app`

## 画像送信失敗時の挙動

- Cloudinary設定不足・アップロード失敗時：
  - 画像送信をスキップ
  - LINEへテキストのみ送信
  - 回答保存と画面表示は継続（アプリは停止しない）

## Streamlit Community Cloud に載せるときの注意

1. リポジトリに `app.py`, `pages/`, `utils/`, `requirements.txt` を含めてpush
2. Community Cloudは `streamlit run app.py` 相当で起動
3. SQLiteはコンテナローカル保存のため、再デプロイ・再起動でデータが消える可能性あり
4. 長期運用時は外部DB移行を推奨
5. 認証なし運用のため、公開範囲は限定

## iPhoneで使う方法（Safari）

1. SafariでアプリURLを開く
2. 共有メニューから「ホーム画面に追加」
3. ホーム画面アイコンから起動して記録

このMVPは1カラム前提で、iPhoneでの入力・閲覧を優先しています。
