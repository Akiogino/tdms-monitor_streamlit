from __future__ import annotations

import os
import secrets
from datetime import datetime

import cloudinary
import cloudinary.uploader
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


def _read_secret(key: str) -> str:
    try:
        value = st.secrets.get(key, "")
    except Exception:
        value = ""

    if value:
        return str(value).strip()

    return os.getenv(key, "").strip()


def get_cloudinary_state() -> tuple[bool, str]:
    cloud_name = _read_secret("CLOUDINARY_CLOUD_NAME")
    api_key = _read_secret("CLOUDINARY_API_KEY")
    api_secret = _read_secret("CLOUDINARY_API_SECRET")

    missing: list[str] = []
    if not cloud_name:
        missing.append("CLOUDINARY_CLOUD_NAME")
    if not api_key:
        missing.append("CLOUDINARY_API_KEY")
    if not api_secret:
        missing.append("CLOUDINARY_API_SECRET")

    if missing:
        return False, f"Cloudinary設定が未完了です: {', '.join(missing)}"

    return True, "Cloudinary送信の準備ができています。"


def _configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=_read_secret("CLOUDINARY_CLOUD_NAME"),
        api_key=_read_secret("CLOUDINARY_API_KEY"),
        api_secret=_read_secret("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def _prepare_line_image_figure(fig) -> go.Figure:
    """
    LINE送信用に、文字化け回避と視認性向上のための見た目調整を行う。

    - 注釈は英語ラベルへ置換（日本語フォント依存を避ける）
    - 線・点・文字サイズを拡大
    """
    line_fig = go.Figure(fig)

    annotation_text_map = {
        "快適": "Comfort",
        "不快": "Discomfort",
        "覚醒高": "High Arousal",
        "覚醒低": "Low Arousal",
        "活性高": "High Vitality",
        "安定高": "High Stability",
        "覚醒高方向": "Arousal +",
        "覚醒低方向": "Arousal -",
    }

    annotations = list(line_fig.layout.annotations or [])
    for annotation in annotations:
        original_text = str(annotation.text)
        annotation.text = annotation_text_map.get(original_text, original_text)
        annotation.font = {"size": 28, "color": "#444444", "family": "Arial, sans-serif"}

    line_fig.update_layout(
        annotations=annotations,
        margin={"l": 40, "r": 40, "t": 40, "b": 40},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )

    for trace in line_fig.data:
        mode = str(getattr(trace, "mode", ""))
        if "lines" in mode and getattr(trace, "line", None):
            line_width = getattr(trace.line, "width", 2) or 2
            trace.line.width = max(float(line_width), 3.0)

        if "markers" in mode and getattr(trace, "marker", None):
            marker_size = getattr(trace.marker, "size", 10) or 10
            if isinstance(marker_size, (int, float)):
                # 現在点(赤)をより強調し、履歴点も見やすくする。
                if getattr(trace.marker, "color", "") == "#d84a4a":
                    trace.marker.size = max(float(marker_size), 30.0)
                    trace.marker.line = {"width": 2, "color": "#ffffff"}
                else:
                    trace.marker.size = max(float(marker_size), 18.0)

    return line_fig


def fig_to_png_bytes(fig) -> bytes:
    """Plotly FigureをPNG bytesへ変換する。"""
    line_fig = _prepare_line_image_figure(fig)
    return pio.to_image(line_fig, format="png", width=1400, height=1400, scale=2)


def build_public_id(user_type: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = secrets.token_hex(4)
    return f"{user_type}-{timestamp}-{random_suffix}"


def upload_png_bytes_to_cloudinary(png_bytes: bytes, public_id: str) -> str:
    """PNG bytesをCloudinaryへアップロードしてsecure_urlを返す。"""
    _configure_cloudinary()

    upload_result = cloudinary.uploader.upload(
        png_bytes,
        resource_type="image",
        folder="tdms-monitor",
        public_id=public_id,
        overwrite=True,
    )

    secure_url = upload_result.get("secure_url")
    if not secure_url:
        raise ValueError("Cloudinaryのsecure_url取得に失敗しました。")

    return str(secure_url)
