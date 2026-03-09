from __future__ import annotations

import streamlit as st

from utils.db import fetch_responses, init_db, insert_response
from utils.diagram import create_mood_diagram
from utils.navigation import render_sidebar_navigation
from utils.scoring import (
    QUESTION_ITEMS,
    SCALE_LABELS,
    build_score_report,
    calculate_scores,
    validate_answers,
)

USER_TYPE = "self"
PAGE_NAME = "回答（秋山用）"


def inject_page_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 760px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 3rem;
            font-size: 1.05rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("二次元気分尺度 モニタリング")
    st.caption("気分を記録し、採点し、こころのダイアグラムで振り返る")
    st.subheader(PAGE_NAME)


def display_text(value: object) -> str:
    if value is None:
        return "（未入力）"

    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return "（未入力）"

    return text


def render_legend() -> None:
    st.caption(
        " / ".join(f"{score} = {label}" for score, label in SCALE_LABELS.items())
    )


def render_form() -> tuple[bool, str, dict[str, object], str]:
    with st.form("akiyama_response_form", clear_on_submit=True):
        context_text = st.text_input(
            "状況（任意）",
            placeholder="例: 運動を始める前、仕事のあと",
        )

        st.write("（　）のあなたの気持ちは、以下の言葉にどれくらい当てはまりますか。近い数字を選んでください。")
        render_legend()

        answers: dict[str, object] = {}
        for key, label in QUESTION_ITEMS:
            answers[key] = st.radio(
                label,
                options=list(SCALE_LABELS.keys()),
                index=None,
                horizontal=True,
            )
            st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)

        free_text = st.text_area(
            "自由記述（任意）",
            placeholder="今の気分や出来事、気になったことを自由にメモ",
            height=120,
        )

        submitted = st.form_submit_button("保存する", width="stretch")

    return submitted, context_text.strip(), answers, free_text.strip()


def save_response(
    submitted: bool,
    context_text: str,
    answers: dict[str, object],
    free_text: str,
) -> None:
    if not submitted:
        return

    is_valid, error_message = validate_answers(answers)
    if not is_valid:
        st.error(error_message or "入力内容を確認してください。")
        return

    typed_answers = {key: int(answers[key]) for key, _ in QUESTION_ITEMS}
    scores = calculate_scores(typed_answers)

    insert_response(
        user_type=USER_TYPE,
        context_text=context_text,
        answers=typed_answers,
        free_text=free_text,
        scores=scores,
    )

    st.success("保存しました")


def render_latest_result() -> None:
    latest_df = fetch_responses(user_type=USER_TYPE, limit=6)

    st.divider()
    st.markdown("### 最新結果")

    if latest_df.empty:
        st.info("まだ回答がありません。")
        return

    latest = latest_df.iloc[0]
    st.write(f"状況: {display_text(latest['context_text'])}")
    score_v = int(latest["score_v"])
    score_s = int(latest["score_s"])
    score_p = int(latest["score_p"])
    score_a = int(latest["score_a"])

    recent_vs = [
        (int(row["score_v"]), int(row["score_s"]))
        for _, row in latest_df.iloc[1:6].iterrows()
    ]

    figure = create_mood_diagram(score_v=score_v, score_s=score_s, recent_vs=recent_vs)
    report_text = build_score_report(
        created_at=display_text(latest["created_at"]),
        score_v=score_v,
        score_s=score_s,
        score_p=score_p,
        score_a=score_a,
    )

    col_chart, col_report = st.columns([1.8, 1.2])
    with col_chart:
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
    with col_report:
        st.markdown("**因子得点**")
        st.text(report_text)

    st.markdown("**自由記述**")
    st.write(display_text(latest["free_text"]))


def main() -> None:
    init_db()
    render_sidebar_navigation()

    inject_page_css()
    render_header()

    submitted, context_text, answers, free_text = render_form()
    save_response(submitted, context_text, answers, free_text)
    render_latest_result()


if __name__ == "__main__":
    main()
