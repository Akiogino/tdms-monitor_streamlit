from __future__ import annotations

import os
import secrets
from datetime import datetime

import cloudinary
import cloudinary.uploader
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


def fig_to_png_bytes(fig) -> bytes:
    """Plotly FigureをPNG bytesへ変換する。"""
    return pio.to_image(fig, format="png", width=700, height=700, scale=2)


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
