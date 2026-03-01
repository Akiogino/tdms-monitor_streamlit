# 二次元気分尺度 モニタリング（Streamlit MVP）

iPhone Safari でも回答しやすい、二次元気分尺度の記録アプリです。

- 8項目に 0〜5 で回答
- 回答直後に V / S / P / A を採点
- こころのダイアグラム（菱形）を表示
- 自由記述を保存
- 履歴（直近20件）と時系列グラフを表示
- CSV ダウンロード対応

## 技術スタック

- Python
- Streamlit (multipage app)
- Plotly
- SQLite
- pandas

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
│   ├── navigation.py
│   ├── scoring.py
│   └── scope.py
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

## Multipage app の説明

サイドバーから以下へ移動できます。

- 回答（自分用）: `user_type = "self"`
- 回答（友人用）: `user_type = "friend"`
- 履歴（自分用）: `self` の履歴のみ表示
- 履歴（友人用）: `friend` の履歴のみ表示

## 自分用ページと友人用ページの違い

- 保存時に `user_type` を分けて保存します。
- 履歴表示と CSV 出力は、それぞれの `user_type` のみ対象です。
- 認証は未実装なので、URLを知っていればアクセス可能です（MVP仕様）。

## 2URL運用しやすくする設定（推奨）

このアプリは `APP_SCOPE` で公開対象を切り替えられます。

- `APP_SCOPE=self` : 自分用ページのみ表示/アクセス許可
- `APP_SCOPE=friend` : 友人用ページのみ表示/アクセス許可
- `APP_SCOPE=all` : 全ページ表示（ローカル確認向け、デフォルト）

### ローカルでの確認例

- 自分用モード

```bash
APP_SCOPE=self streamlit run app.py
```

- 友人用モード

```bash
APP_SCOPE=friend streamlit run app.py
```

### Streamlit Community Cloud で2URLにする手順

同じGitHubリポジトリから、アプリを2つ作成します（どちらも Main file は `app.py`）。

1. アプリAを作成し、Secrets に `APP_SCOPE="self"` を設定（自分用URL）
2. アプリBを作成し、Secrets に `APP_SCOPE="friend"` を設定（友人用URL）
3. それぞれ発行されたURLを使い分ける

`.streamlit/config.toml` でデフォルトのページ一覧を非表示にし、スコープに合う導線だけをサイドバー表示します。

## Streamlit Community Cloud に載せるときの注意

1. リポジトリに `app.py`, `pages/`, `utils/`, `requirements.txt` を含めて push する。
2. Community Cloud は `streamlit run app.py` 相当で起動される。
3. 2URL運用する場合は、同一リポジトリからアプリを2つ作り、Secrets の `APP_SCOPE` をそれぞれ `self` / `friend` に設定する。
4. SQLite はコンテナのローカル保存なので、再デプロイや再起動でデータが消える可能性がある。
5. 長期運用する場合は、将来的に外部DBへ移行する。
6. 認証なし運用のため、公開範囲は限定する。

## iPhone で使う方法（Safari）

1. Safari でアプリURLを開く
2. 共有メニューから「ホーム画面に追加」
3. ホーム画面アイコンから起動して記録

このMVPは1カラム前提で、iPhoneでの入力・閲覧を優先しています。
