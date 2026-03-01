from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.db import CSV_EXPORT_COLUMNS, fetch_responses, init_db
from utils.diagram import create_score_timeseries_figure
from utils.navigation import render_sidebar_navigation
from utils.scope import enforce_user_scope, get_app_scope

USER_TYPE = "friend"
PAGE_NAME = "履歴（友人用）"
DISPLAY_COLUMNS = [
    "created_at",
    "context_text",
    "score_v",
    "score_s",
    "score_p",
    "score_a",
    "free_text",
]


def inject_page_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 900px;
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
    st.subheader(PAGE_NAME)


def build_csv(df: pd.DataFrame) -> bytes:
    csv_df = df[CSV_EXPORT_COLUMNS].copy()
    return csv_df.to_csv(index=False).encode("utf-8-sig")


def main() -> None:
    scope = get_app_scope()
    init_db()
    render_sidebar_navigation(scope)
    enforce_user_scope(scope, USER_TYPE)

    inject_page_css()
    render_header()

    df = fetch_responses(user_type=USER_TYPE, limit=20)

    if df.empty:
        st.info("まだ履歴がありません。")
        return

    st.markdown("### 直近20件")
    table_df = df[DISPLAY_COLUMNS].copy().fillna("")
    table_df = table_df.rename(
        columns={
            "score_v": "V",
            "score_s": "S",
            "score_p": "P",
            "score_a": "A",
        }
    )
    st.dataframe(table_df, width="stretch", hide_index=True)

    st.download_button(
        "CSVダウンロード",
        data=build_csv(df),
        file_name="mood_friend_history.csv",
        mime="text/csv",
        width="stretch",
    )

    st.markdown("### スコア時系列")
    figure = create_score_timeseries_figure(df)
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})


if __name__ == "__main__":
    main()
