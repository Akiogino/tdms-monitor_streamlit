from __future__ import annotations

import streamlit as st

def render_sidebar_navigation() -> None:
    st.sidebar.markdown("## メニュー")
    st.sidebar.page_link("app.py", label="トップ", icon="🏠")
    st.sidebar.page_link("pages/1_回答_自分用.py", label="回答（秋山用）", icon="📝")
    st.sidebar.page_link("pages/3_履歴_自分用.py", label="履歴（秋山用）", icon="📈")
    st.sidebar.page_link("pages/2_回答_友人用.py", label="回答（明石用）", icon="📝")
    st.sidebar.page_link("pages/4_履歴_友人用.py", label="履歴（明石用）", icon="📈")
