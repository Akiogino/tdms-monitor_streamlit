from __future__ import annotations

import logging
from datetime import datetime

import streamlit as st

from utils.db import fetch_recent_vs_points, fetch_responses, init_db, insert_response
from utils.diagram import create_mood_diagram
from utils.image_hosting import (
    build_public_id,
    fig_to_png_bytes,
    get_cloudinary_state,
    upload_png_bytes_to_cloudinary,
)
from utils.line_messaging import get_line_push_state, push_report
from utils.navigation import render_sidebar_navigation
from utils.scoring import (
    QUESTION_ITEMS,
    SCALE_LABELS,
    build_line_report_text,
    build_score_report,
    calculate_scores,
    validate_answers,
)

logger = logging.getLogger(__name__)

USER_TYPE = "friend"
PAGE_NAME = "回答（明石用）"


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


def render_form(
    line_ready: bool,
    line_message: str,
    cloudinary_ready: bool,
    cloudinary_message: str,
) -> tuple[bool, str, dict[str, object], str, bool]:
    if not line_ready:
        st.warning(f"LINE送信は無効です: {line_message}")
    elif not cloudinary_ready:
        st.info(f"画像送信は無効です（テキストのみ送信）: {cloudinary_message}")

    with st.form("akashi_response_form", clear_on_submit=True):
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

        send_to_line = st.toggle(
            "送信後にLINEへレポート送信",
            value=line_ready,
            disabled=not line_ready,
        )

        submitted = st.form_submit_button("保存する", width="stretch")

    return submitted, context_text.strip(), answers, free_text.strip(), bool(send_to_line)


def save_response(
    submitted: bool,
    context_text: str,
    answers: dict[str, object],
    free_text: str,
    send_to_line: bool,
    cloudinary_ready: bool,
) -> None:
    if not submitted:
        return

    is_valid, error_message = validate_answers(answers)
    if not is_valid:
        st.error(error_message or "入力内容を確認してください。")
        return

    typed_answers = {key: int(answers[key]) for key, _ in QUESTION_ITEMS}
    scores = calculate_scores(typed_answers)

    # 保存前の直近点を薄い履歴点として使う。
    history_vs = fetch_recent_vs_points(user_type=USER_TYPE, limit=5)

    insert_response(
        user_type=USER_TYPE,
        context_text=context_text,
        answers=typed_answers,
        free_text=free_text,
        scores=scores,
    )

    st.success("保存しました")

    if not send_to_line:
        return

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_df = fetch_responses(user_type=USER_TYPE, limit=1)
    if not latest_df.empty:
        created_at = str(latest_df.iloc[0]["created_at"])

    figure = create_mood_diagram(
        score_v=scores["score_v"],
        score_s=scores["score_s"],
        recent_vs=history_vs,
    )

    report_text = build_line_report_text(
        responder_label="明石",
        created_at=created_at,
        context_text=context_text,
        free_text=free_text,
        score_v=scores["score_v"],
        score_s=scores["score_s"],
        score_p=scores["score_p"],
        score_a=scores["score_a"],
    )

    image_url: str | None = None
    if cloudinary_ready:
        try:
            png_bytes = fig_to_png_bytes(figure)
            public_id = build_public_id(USER_TYPE)
            image_url = upload_png_bytes_to_cloudinary(png_bytes=png_bytes, public_id=public_id)
        except Exception as exc:
            logger.exception("Cloudinary upload failed for %s", USER_TYPE)
            st.warning(
                f"ダイアグラム画像の送信に失敗したため、LINEへはテキストのみ送信します。詳細: {exc}"
            )

    sent, message = push_report(user_type=USER_TYPE, image_url=image_url, report_text=report_text)
    if sent:
        st.toast("LINEにレポートを送信しました。")
    else:
        st.warning(f"LINE送信に失敗しました: {message}")


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

    line_ready, line_message = get_line_push_state(USER_TYPE)
    cloudinary_ready, cloudinary_message = get_cloudinary_state()

    submitted, context_text, answers, free_text, send_to_line = render_form(
        line_ready=line_ready,
        line_message=line_message,
        cloudinary_ready=cloudinary_ready,
        cloudinary_message=cloudinary_message,
    )
    save_response(
        submitted=submitted,
        context_text=context_text,
        answers=answers,
        free_text=free_text,
        send_to_line=send_to_line,
        cloudinary_ready=cloudinary_ready,
    )
    render_latest_result()


if __name__ == "__main__":
    main()
