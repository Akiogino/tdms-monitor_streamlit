from __future__ import annotations

import streamlit as st

from utils.scope import scope_label


def render_sidebar_navigation(scope: str) -> None:
    st.sidebar.markdown("## メニュー")
    st.sidebar.page_link("app.py", label="トップ", icon="🏠")

    if scope in {"all", "self"}:
        st.sidebar.page_link("pages/1_回答_自分用.py", label="回答（自分用）", icon="📝")
        st.sidebar.page_link("pages/3_履歴_自分用.py", label="履歴（自分用）", icon="📈")

    if scope in {"all", "friend"}:
        st.sidebar.page_link("pages/2_回答_友人用.py", label="回答（友人用）", icon="📝")
        st.sidebar.page_link("pages/4_履歴_友人用.py", label="履歴（友人用）", icon="📈")

    st.sidebar.caption(f"公開モード: {scope_label(scope)}")
