"""Search page: look up additives by E-number, INS number, or name."""

import streamlit as st

from src.db.queries import search_by_code, search_by_name
from src.ui.components.additive_card import render_additive_card


def render_search_page(db_path: str) -> None:
    """Render the search page."""
    st.header("Search Food Additives")

    search_mode = st.radio(
        "Search by:",
        ["E-Number / INS Number", "Name"],
        horizontal=True,
    )

    if search_mode == "E-Number / INS Number":
        input_code = st.text_input(
            "Enter additive number (e.g., 102, E621, INS 100):",
            max_chars=10,
            placeholder="e.g. 102",
        )

        if st.button("Search", type="primary"):
            if not input_code.strip():
                st.warning("Please enter a number.")
                return

            result = search_by_code(db_path, input_code)
            if result:
                render_additive_card(result)
            else:
                st.error(f"No additive found for '{input_code}'.")

    else:
        name_query = st.text_input(
            "Enter additive name (partial match):",
            max_chars=100,
            placeholder="e.g. curcumin, tartrazine",
        )

        if st.button("Search", type="primary"):
            if not name_query.strip():
                st.warning("Please enter a name.")
                return

            results = search_by_name(db_path, name_query)
            if results:
                st.success(f"Found {len(results)} result(s).")
                for result in results:
                    render_additive_card(result)
            else:
                st.error(f"No additives found matching '{name_query}'.")
