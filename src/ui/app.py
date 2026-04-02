"""Streamlit application entry point.

Routes between Search, Analytics, Browse, and Math Plotter pages.
"""

import streamlit as st

from src.db.connection import ensure_database, get_db_path
from src.ui.pages.analytics import render_analytics_page
from src.ui.pages.browse import render_browse_page
from src.ui.pages.math_plotter import render_math_plotter_page
from src.ui.pages.reverse_subtract import render_reverse_subtract_page
from src.ui.pages.search import render_search_page


def main() -> None:
    st.set_page_config(
        page_title="Food Additive Lookup",
        page_icon="🍽️",  # noqa: RUF001
        layout="wide",
    )

    st.title("Food Additive Lookup")
    st.caption("E-Number & INS Additive Database - Vegan, Vegetarian, Halal & Safety Info")

    # Ensure database exists
    db_path = get_db_path()
    try:
        ensure_database(db_path)
    except Exception as e:
        st.error(f"Database error: {e}. Run `python -m src.etl.build_database` first.")
        return

    # Navigation
    st.sidebar.header("Food Additives")
    page = st.sidebar.radio(
        "Navigation",
        ["Search", "Analytics", "Browse"],
        index=0,
    )

    st.sidebar.divider()
    st.sidebar.header("Tools")
    tools_page = st.sidebar.radio(
        "Other Tools",
        ["None", "Math Plotter", "Reverse Subtraction"],
        index=0,
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "Build the database:\n"
        "```\npython -m src.etl.build_database\n```"
    )

    # Tools take priority when selected
    if tools_page == "Math Plotter":
        render_math_plotter_page()
    elif tools_page == "Reverse Subtraction":
        render_reverse_subtract_page()
    elif page == "Search":
        render_search_page(db_path)
    elif page == "Analytics":
        render_analytics_page(db_path)
    elif page == "Browse":
        render_browse_page(db_path)


if __name__ == "__main__":
    main()
