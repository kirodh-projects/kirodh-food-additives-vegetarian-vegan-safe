"""Streamlit application entry point.

Routes between Food Additives, Species Taxonomy, and Tools sections.
"""

import streamlit as st

from src.db.connection import ensure_database, get_db_path
from src.ui.pages.analytics import render_analytics_page
from src.ui.pages.browse import render_browse_page
from src.ui.pages.math_plotter import render_math_plotter_page
from src.ui.pages.reverse_subtract import render_reverse_subtract_page
from src.ui.pages.search import render_search_page
from src.ui.pages.species import render_species_page


def main() -> None:
    st.set_page_config(
        page_title="Kirodh's Tinkering Lab",
        page_icon="🔬",  # noqa: RUF001
        layout="wide",
    )

    # Ensure food additives database exists
    db_path = get_db_path()
    try:
        ensure_database(db_path)
    except Exception as e:
        st.error(f"Database error: {e}. Run `python -m src.etl.build_database` first.")

    # --- Sidebar navigation ---
    section = st.sidebar.selectbox(
        "Section",
        ["Food Additives", "Species Taxonomy", "Tools"],
        index=0,
    )

    if section == "Food Additives":
        st.sidebar.divider()
        page = st.sidebar.radio(
            "Page",
            ["Search", "Analytics", "Browse"],
        )
        st.sidebar.divider()
        st.sidebar.caption("```\npython -m src.etl.build_database\n```")

        st.title("Food Additive Lookup")
        st.caption("E-Number & INS Additive Database - Vegan, Vegetarian, Halal & Safety Info")

        if page == "Search":
            render_search_page(db_path)
        elif page == "Analytics":
            render_analytics_page(db_path)
        elif page == "Browse":
            render_browse_page(db_path)

    elif section == "Species Taxonomy":
        st.sidebar.divider()
        st.sidebar.caption("```\npython -m src.etl.build_species_db\n```")
        render_species_page()

    elif section == "Tools":
        st.sidebar.divider()
        tool = st.sidebar.radio(
            "Tool",
            ["Math Plotter", "Reverse Subtraction"],
        )

        if tool == "Math Plotter":
            render_math_plotter_page()
        elif tool == "Reverse Subtraction":
            render_reverse_subtract_page()


if __name__ == "__main__":
    main()
