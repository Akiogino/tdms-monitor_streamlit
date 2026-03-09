from __future__ import annotations

import logging
import os
from typing import Any

import requests
import streamlit as st

LINE_PUSH_ENDPOINT = "https://api.line.me/v2/bot/message/push"

logger = logging.getLogger(__name__)


def _read_secret(key: str) -> str:
    try:
        value = st.secrets.get(key, "")
    except Exception:
        value = ""

    if value:
        return str(value).strip()

    return os.getenv(key, "").strip()


def _resolve_target_user_id(user_type: str) -> str:
    if user_type == "self":
        return _read_secret("LINE_USER_ID_SELF")
    if user_type == "friend":
        return _read_secret("LINE_USER_ID_FRIEND")
    return ""


def get_line_push_state(user_type: str) -> tuple[bool, str]:
    """LINE Push送信の有効状態を返す。"""
    token = _read_secret("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        return False, "LINE_CHANNEL_ACCESS_TOKEN が未設定です。"

    target_user_id = _resolve_target_user_id(user_type)
    if not target_user_id:
        if user_type == "self":
            return False, "LINE_USER_ID_SELF が未設定です。"
        if user_type == "friend":
            return False, "LINE_USER_ID_FRIEND が未設定です。"
        return False, "LINE送信先ユーザーIDが未設定です。"

    return True, "LINE送信の準備ができています。"


def push_report(user_type: str, image_url: str | None, report_text: str) -> tuple[bool, str]:
    """LINEに画像(任意)とテキストをPush送信する。"""
    is_ready, message = get_line_push_state(user_type)
    if not is_ready:
        logger.warning("LINE push skipped: %s", message)
        return False, message

    token = _read_secret("LINE_CHANNEL_ACCESS_TOKEN")
    target_user_id = _resolve_target_user_id(user_type)

    messages: list[dict[str, Any]] = []
    if image_url:
        messages.append(
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url,
            }
        )

    messages.append(
        {
            "type": "text",
            "text": report_text[:4900],
        }
    )

    payload = {
        "to": target_user_id,
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            LINE_PUSH_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.exception("LINE push request failed")
        return False, f"LINE APIへの接続に失敗しました: {exc}"

    if response.status_code >= 400:
        logger.error("LINE push failed: status=%s body=%s", response.status_code, response.text)
        return False, f"LINE送信に失敗しました ({response.status_code})"

    return True, "LINEに送信しました。"
