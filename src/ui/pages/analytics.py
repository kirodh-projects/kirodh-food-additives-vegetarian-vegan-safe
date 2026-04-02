"""Analytics dashboard page with charts and statistics."""

import pandas as pd
import streamlit as st

from src.db.queries import get_analytics_summary, get_category_vegan_breakdown, get_dangerous_additives
from src.ui.components.charts import (
    HALAL_COLORS,
    ORIGIN_COLORS,
    SAFETY_COLORS,
    VEGAN_COLORS,
    make_bar_chart,
    make_pie_chart,
    make_stacked_bar,
)


def render_analytics_page(db_path: str) -> None:
    """Render the analytics dashboard."""
    st.header("Analytics Dashboard")

    summary = get_analytics_summary(db_path)
    total = summary["total"]

    if total == 0:
        st.warning("No data in database. Run the database builder first.")
        return

    # --- Metric cards ---
    _render_metrics(summary, total)

    st.divider()

    # --- Dietary status charts ---
    st.subheader("Dietary Classification")
    col1, col2 = st.columns(2)

    with col1:
        vegan_data = summary.get("vegan_status", {})
        if vegan_data:
            fig = make_pie_chart(vegan_data, "Vegan Status Distribution", VEGAN_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        veg_data = summary.get("vegetarian_status", {})
        if veg_data:
            fig = make_pie_chart(veg_data, "Vegetarian Status Distribution (Lacto)", VEGAN_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        halal_data = summary.get("halal_status", {})
        if halal_data:
            fig = make_pie_chart(halal_data, "Halal Status Distribution", HALAL_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        origin_data = summary.get("origin", {})
        if origin_data:
            fig = make_pie_chart(origin_data, "Origin Distribution", ORIGIN_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Safety analysis ---
    st.subheader("Safety Analysis")
    col1, col2 = st.columns(2)

    with col1:
        safety_data = summary.get("safety_level", {})
        if safety_data:
            fig = make_bar_chart(safety_data, "Safety Level Breakdown", SAFETY_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        origin_data = summary.get("origin", {})
        if origin_data:
            fig = make_bar_chart(origin_data, "Origin Breakdown", ORIGIN_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    # --- Dangerous additives ---
    st.subheader("Dangerous Additives (Avoid / Banned)")
    dangerous = get_dangerous_additives(db_path)
    if dangerous:
        df = pd.DataFrame(dangerous)
        display_cols = ["e_number", "common_name", "safety_level", "category", "origin", "description"]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[available_cols],
            use_container_width=True,
            height=min(400, 40 + len(dangerous) * 35),
        )
    else:
        st.success("No dangerous additives found in the database.")

    st.divider()

    # --- Category breakdown ---
    st.subheader("Category Analysis")
    category_data = summary.get("category", {})
    if category_data:
        # Top 15 categories by count
        sorted_cats = dict(sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:15])
        fig = make_bar_chart(sorted_cats, "Top 15 Categories by Count", horizontal=False)
        st.plotly_chart(fig, use_container_width=True)

    # Category vs vegan stacked bar
    breakdown_data = get_category_vegan_breakdown(db_path)
    if breakdown_data:
        df = pd.DataFrame(breakdown_data)
        # Filter to top 10 categories for readability
        if category_data:
            top_cats = list(dict(sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:10]).keys())
            df = df[df["category"].isin(top_cats)]

        if not df.empty:
            fig = make_stacked_bar(
                df, "category", "vegan_status",
                "Vegan Status by Category (Top 10)",
                VEGAN_COLORS,
            )
            st.plotly_chart(fig, use_container_width=True)


def _render_metrics(summary: dict, total: int) -> None:
    """Render the top metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Additives", total)

    with col2:
        vegan_yes = summary.get("vegan_status", {}).get("Yes", 0)
        pct = f"{vegan_yes / total * 100:.1f}%" if total else "0%"
        st.metric("Vegan-Friendly", f"{vegan_yes} ({pct})")

    with col3:
        safe_count = summary.get("safety_level", {}).get("Safe", 0)
        pct = f"{safe_count / total * 100:.1f}%" if total else "0%"
        st.metric("Safe", f"{safe_count} ({pct})")

    with col4:
        eu_count = summary.get("approval_eu", 0)
        pct = f"{eu_count / total * 100:.1f}%" if total else "0%"
        st.metric("EU Approved", f"{eu_count} ({pct})")

    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        veg_yes = summary.get("vegetarian_status", {}).get("Yes", 0)
        pct = f"{veg_yes / total * 100:.1f}%" if total else "0%"
        st.metric("Vegetarian-Friendly", f"{veg_yes} ({pct})")

    with col2:
        halal_count = summary.get("halal_status", {}).get("Halal", 0)
        pct = f"{halal_count / total * 100:.1f}%" if total else "0%"
        st.metric("Halal", f"{halal_count} ({pct})")

    with col3:
        banned = summary.get("banned_count", 0)
        st.metric("Banned Somewhere", banned)

    with col4:
        synthetic = summary.get("origin", {}).get("Synthetic", 0)
        pct = f"{synthetic / total * 100:.1f}%" if total else "0%"
        st.metric("Synthetic", f"{synthetic} ({pct})")
