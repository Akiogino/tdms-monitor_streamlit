from __future__ import annotations

import os

import streamlit as st

ALLOWED_SCOPES = {"all", "self", "friend"}


def _normalize_scope(value: object) -> str:
    text = str(value).strip().lower()
    return text.strip("\"'")


def get_app_scope() -> str:
    """APP_SCOPE(環境変数/Secrets)から公開スコープを取得する。"""
    # Community CloudではSecrets指定を優先し、環境変数はフォールバックで使う。
    try:
        secret_scope = _normalize_scope(st.secrets.get("APP_SCOPE", ""))
    except Exception:
        secret_scope = ""

    if secret_scope in ALLOWED_SCOPES:
        return secret_scope

    env_scope = _normalize_scope(os.getenv("APP_SCOPE", ""))
    if env_scope in ALLOWED_SCOPES:
        return env_scope

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
