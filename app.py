from __future__ import annotations

import streamlit as st

from utils.db import DB_PATH, init_db
from utils.navigation import render_sidebar_navigation


def inject_base_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 760px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("二次元気分尺度 モニタリング")
    st.caption("気分を記録し、採点し、こころのダイアグラムで振り返る")


def main() -> None:
    st.set_page_config(page_title="二次元気分尺度 モニタリング", page_icon="🧭", layout="centered")
    init_db()

    render_sidebar_navigation()

    inject_base_css()
    render_header()

    st.markdown("### 使い方")
    st.markdown(
        """
- サイドバーからページを選択してください。
- 回答は「秋山用」と「明石用」で分かれて保存されます。
- 履歴ページでは直近20件の表示、CSVダウンロード、時系列グラフが使えます。
        """
    )

    st.markdown("### ページ構成")
    st.markdown(
        """
- 回答（秋山用）
- 回答（明石用）
- 履歴（秋山用）
- 履歴（明石用）
        """
    )

    st.info("iPhone Safari での利用を想定した1カラムUIです。")
    st.caption(f"SQLite DB: {DB_PATH}")


if __name__ == "__main__":
    main()
