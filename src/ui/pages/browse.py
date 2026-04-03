"""Browse page: filterable, paginated table of all additives."""

import pandas as pd
import streamlit as st

from src.db.queries import get_all_additives, get_distinct_values, get_total_count


DISPLAY_COLUMNS = [
    "e_number", "ins_number", "common_name", "category",
    "vegan_status", "vegetarian_status", "halal_status",
    "safety_level", "origin",
]

PAGE_SIZE = 50


def render_browse_page(db_path: str) -> None:
    """Render the browse/filter page."""
    st.header("Browse All Additives")

    # --- Filters ---
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            categories = get_distinct_values(db_path, "category")
            selected_cats = st.multiselect("Category", categories)

            vegan_opts = get_distinct_values(db_path, "vegan_status")
            selected_vegan = st.multiselect("Vegan Status", vegan_opts)

        with col2:
            veg_opts = get_distinct_values(db_path, "vegetarian_status")
            selected_veg = st.multiselect("Vegetarian Status", veg_opts)

            halal_opts = get_distinct_values(db_path, "halal_status")
            selected_halal = st.multiselect("Halal Status", halal_opts)

        with col3:
            safety_opts = get_distinct_values(db_path, "safety_level")
            selected_safety = st.multiselect("Safety Level", safety_opts)

            origin_opts = get_distinct_values(db_path, "origin")
            selected_origin = st.multiselect("Origin", origin_opts)

    # Build filters dict
    filters = {}
    if selected_cats:
        filters["category"] = selected_cats
    if selected_vegan:
        filters["vegan_status"] = selected_vegan
    if selected_veg:
        filters["vegetarian_status"] = selected_veg
    if selected_halal:
        filters["halal_status"] = selected_halal
    if selected_safety:
        filters["safety_level"] = selected_safety
    if selected_origin:
        filters["origin"] = selected_origin

    # --- Sort ---
    sort_col = st.selectbox(
        "Sort by",
        ["e_number", "common_name", "category", "safety_level", "vegan_status"],
        index=0,
    )

    # --- Pagination ---
    total = get_total_count(db_path, filters if filters else None)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{total}** additives found")
    with col2:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    offset = (page - 1) * PAGE_SIZE

    # --- Data table ---
    records = get_all_additives(
        db_path,
        filters=filters if filters else None,
        sort_by=sort_col,
        limit=PAGE_SIZE,
        offset=offset,
    )

    if records:
        df = pd.DataFrame(records)
        available_cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
        st.dataframe(
            df[available_cols],
            width="stretch",
            height=min(600, 40 + len(records) * 35),
        )

        # CSV export
        csv_data = df[available_cols].to_csv(index=False)
        st.download_button(
            "Export as CSV",
            csv_data,
            "food_additives_filtered.csv",
            "text/csv",
        )
    else:
        st.info("No additives match the selected filters.")

    st.caption(f"Page {page} of {total_pages}")
