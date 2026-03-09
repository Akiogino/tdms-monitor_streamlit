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

## Multipage app の説明

サイドバーから以下へ移動できます。

- 回答（秋山用）: `user_type = "self"` として保存
- 回答（明石用）: `user_type = "friend"` として保存
- 履歴（秋山用）: 秋山用データのみ表示
- 履歴（明石用）: 明石用データのみ表示

## Streamlit Community Cloud に載せるときの注意

1. リポジトリに `app.py`, `pages/`, `utils/`, `requirements.txt` を含めて push する。
2. Community Cloud は `streamlit run app.py` 相当で起動される。
3. SQLite はコンテナのローカル保存なので、再デプロイや再起動でデータが消える可能性がある。
4. 長期運用する場合は、将来的に外部DBへ移行する。
5. 認証なし運用のため、公開範囲は限定する。

## iPhone で使う方法（Safari）

1. Safari でアプリURLを開く
2. 共有メニューから「ホーム画面に追加」
3. ホーム画面アイコンから起動して記録

このMVPは1カラム前提で、iPhoneでの入力・閲覧を優先しています。
