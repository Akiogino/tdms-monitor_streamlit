from __future__ import annotations

import os

import streamlit as st

ALLOWED_SCOPES = {"all", "self", "friend"}


def get_app_scope() -> str:
    """APP_SCOPE(環境変数/Secrets)から公開スコープを取得する。"""
    scope = os.getenv("APP_SCOPE", "").strip()

    if not scope:
        try:
            raw_secret = st.secrets.get("APP_SCOPE", "")
            scope = str(raw_secret).strip()
        except Exception:
            scope = ""

    scope = scope.lower()
    if scope in ALLOWED_SCOPES:
        return scope

    return "all"


def scope_label(scope: str) -> str:
    mapping = {
        "all": "全ページ公開（ローカル確認向け）",
        "self": "自分用URL",
        "friend": "友人用URL",
    }
    return mapping.get(scope, mapping["all"])


def is_user_allowed(scope: str, user_type: str) -> bool:
    return scope == "all" or scope == user_type


def enforce_user_scope(scope: str, user_type: str) -> None:
    if is_user_allowed(scope, user_type):
        return

    allowed_label = "自分用" if scope == "self" else "友人用"
    st.error(f"このURLは{allowed_label}専用です。サイドバーから利用可能ページへ移動してください。")
    st.stop()
