"""Species taxonomy browser and search page."""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.db.species_connection import list_species_db_files
from src.db.species_queries import (
    browse_species,
    get_species_distinct_values,
    get_species_stats,
    get_species_total_count,
    get_trait_distribution,
    search_species,
)

PAGE_SIZE = 50

KINGDOM_COLORS = {
    "Animalia": "#e74c3c",
    "Plantae": "#2ecc71",
    "Fungi": "#9b59b6",
    "Chromista": "#f39c12",
    "Bacteria": "#3498db",
    "Archaea": "#1abc9c",
    "Protozoa": "#e67e22",
    "Viruses": "#95a5a6",
    "incertae sedis": "#bdc3c7",
    "Unknown": "#bdc3c7",
}


# ── Cached query wrappers ──────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Loading statistics...")
def _cached_stats() -> dict:
    return get_species_stats()


@st.cache_data(ttl=3600, show_spinner="Loading distribution data...")
def _cached_trait_distribution() -> list[dict]:
    return get_trait_distribution()


@st.cache_data(ttl=3600, show_spinner="Loading filter values...")
def _cached_distinct(field: str) -> list[str]:
    return get_species_distinct_values(field)


# ── Page entry point ───────────────────────────────────────────────────

def render_species_page() -> None:
    """Render the species taxonomy page."""
    st.header("Species Taxonomy Database")
    st.caption("GBIF Backbone Taxonomy - Search and browse all known species")

    db_files = list_species_db_files()
    if not db_files:
        st.warning(
            "No species database found. Build it with:\n\n"
            "```\npython -m src.etl.build_species_db\n```\n\n"
            "This downloads the GBIF Backbone Taxonomy (~200MB) and processes it."
        )
        return

    tab_search, tab_browse, tab_dist, tab_guna, tab_stats = st.tabs(
        ["Search", "Browse", "Physical Traits", "Gunas (Purity / Passion / Ignorance)", "Statistics"]
    )

    with tab_search:
        _render_search()

    with tab_browse:
        _render_browse()

    with tab_dist:
        _render_distribution()

    with tab_guna:
        _render_guna_distribution()

    with tab_stats:
        _render_stats()


# ── Search ─────────────────────────────────────────────────────────────

def _render_search() -> None:
    """Search tab."""
    query = st.text_input(
        "Search by name (scientific, genus, or family):",
        placeholder="e.g. Panthera leo, Homo, Felidae",
        max_chars=200,
    )

    if st.button("Search Species", type="primary"):
        if not query.strip():
            st.warning("Enter a search term.")
            return

        results = search_species(query, limit=100)
        if results:
            st.success(f"Found {len(results)} result(s)")
            _display_species_table(results, key_prefix="search")
        else:
            st.error(f"No species found matching '{query}'.")


# ── Browse ─────────────────────────────────────────────────────────────

def _render_browse() -> None:
    """Browse tab with filters and pagination."""
    with st.expander("Filters", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            kingdoms = _cached_distinct("kingdom")
            sel_kingdom = st.multiselect("Kingdom", kingdoms)

            phyla = _cached_distinct("phylum")
            sel_phylum = st.multiselect("Phylum", phyla[:50] if len(phyla) > 50 else phyla)

        with col2:
            sel_family_text = st.text_input("Family (type to filter)", "")

            ranks = _cached_distinct("taxon_rank")
            sel_rank = st.multiselect("Taxon Rank", ranks)

        with col3:
            statuses = _cached_distinct("taxonomic_status")
            sel_status = st.multiselect("Taxonomic Status", statuses)

    filters = {}
    if sel_kingdom:
        filters["kingdom"] = sel_kingdom
    if sel_phylum:
        filters["phylum"] = sel_phylum
    if sel_family_text.strip():
        filters["family"] = [sel_family_text.strip()]
    if sel_rank:
        filters["taxon_rank"] = sel_rank
    if sel_status:
        filters["taxonomic_status"] = sel_status

    sort_col = st.selectbox(
        "Sort by",
        ["scientific_name", "kingdom", "family", "genus", "taxon_rank"],
    )

    total = get_species_total_count(filters=filters if filters else None)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{total:,}** species found")
    with col2:
        page = st.number_input("Page", 1, total_pages, 1, key="species_page")

    offset = (page - 1) * PAGE_SIZE
    records = browse_species(
        filters=filters if filters else None,
        sort_by=sort_col,
        limit=PAGE_SIZE,
        offset=offset,
    )

    if records:
        _display_species_table(records, key_prefix="browse")
    else:
        st.info("No species match the selected filters.")

    st.caption(f"Page {page} of {total_pages:,}")


# ── Species Distribution (ternary plot) ────────────────────────────────

def _render_distribution() -> None:
    """Ternary plot of mobility / warm-bloodedness / size."""
    st.subheader("Species Distribution")
    st.caption(
        "Ternary plot showing the relative proportions of three traits "
        "for each taxonomic class. Each point represents a class, sized "
        "by the number of species it contains and coloured by kingdom."
    )

    data = _cached_trait_distribution()
    if not data:
        st.info("Trait data not available. Re-run the species trait migration.")
        return

    df = pd.DataFrame(data)

    # Kingdom filter
    all_kingdoms = sorted(df["kingdom"].unique())
    selected_kingdoms = st.multiselect(
        "Filter by kingdom",
        all_kingdoms,
        default=all_kingdoms,
        key="ternary_kingdoms",
    )

    if not selected_kingdoms:
        st.warning("Select at least one kingdom.")
        return

    filtered = df[df["kingdom"].isin(selected_kingdoms)].copy()

    # Add epsilon so points with a zero axis are still plotable
    eps = 0.001
    filtered["a"] = filtered["mobility"] + eps
    filtered["b"] = filtered["warm_blood"] + eps
    filtered["c"] = filtered["size"] + eps

    # Marker size: log-scaled species count, clamped to readable range
    filtered["marker_size"] = filtered["count"].apply(
        lambda n: max(4, min(40, 3 * math.log10(max(n, 1)) + 2))
    )

    fig = go.Figure()
    for kingdom in selected_kingdoms:
        kdf = filtered[filtered["kingdom"] == kingdom]
        if kdf.empty:
            continue
        fig.add_trace(go.Scatterternary(
            a=kdf["a"],
            b=kdf["b"],
            c=kdf["c"],
            mode="markers",
            name=kingdom,
            marker=dict(
                size=kdf["marker_size"],
                color=KINGDOM_COLORS.get(kingdom, "#95a5a6"),
                line=dict(width=0.5, color="white"),
                opacity=0.8,
            ),
            text=kdf.apply(
                lambda r: (
                    f"{r['class_name']}<br>"
                    f"{r['kingdom']}<br>"
                    f"Species: {r['count']:,}<br>"
                    f"Mobility: {r['mobility']:.3f}<br>"
                    f"Warm-blood: {r['warm_blood']:.3f}<br>"
                    f"Size: {r['size']:.3f}"
                ),
                axis=1,
            ),
            hoverinfo="text",
        ))

    fig.update_layout(
        ternary=dict(
            aaxis=dict(title="Mobility", min=0),
            baxis=dict(title="Warm-blooded", min=0),
            caxis=dict(title="Size", min=0),
        ),
        height=700,
        margin=dict(t=40, b=40, l=60, r=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )
    st.plotly_chart(fig, width="stretch")

    # Summary table below
    with st.expander("Class details", expanded=False):
        table_df = filtered[["kingdom", "class_name", "count", "mobility", "warm_blood", "size"]].copy()
        table_df = table_df.sort_values("count", ascending=False)
        table_df.columns = ["Kingdom", "Class", "Species Count", "Mobility", "Warm-blooded", "Size"]
        table_df["Species Count"] = table_df["Species Count"].apply(lambda n: f"{n:,}")
        table_df["Mobility"] = table_df["Mobility"].apply(lambda v: f"{v:.3f}")
        table_df["Warm-blooded"] = table_df["Warm-blooded"].apply(lambda v: f"{v:.3f}")
        table_df["Size"] = table_df["Size"].apply(lambda v: f"{v:.3f}")
        st.dataframe(table_df, width="stretch", height=400)


# ── Guna Distribution (ternary plot) ───────────────────────────────────

def _render_guna_distribution() -> None:
    """Ternary plot of Sattva (purity) / Rajas (passion) / Tamas (ignorance)."""
    st.subheader("Guna Distribution")
    st.caption(
        "Ternary plot of the three Gunas from Vedic philosophy. Each taxonomic class "
        "is positioned by its relative composition of **Sattva** (purity, harmony, "
        "nourishment), **Rajas** (passion, activity, desire), and **Tamas** (ignorance, "
        "inertia, darkness). Scores are based on the spiritual and physical nature of "
        "each group: diet, behaviour, habitat, and traditional associations."
    )

    data = _cached_trait_distribution()
    if not data or "purity" not in data[0]:
        st.info("Guna data not available. Run the trait migration to populate.")
        return

    df = pd.DataFrame(data)

    # Kingdom filter
    all_kingdoms = sorted(df["kingdom"].unique())
    selected_kingdoms = st.multiselect(
        "Filter by kingdom",
        all_kingdoms,
        default=all_kingdoms,
        key="guna_kingdoms",
    )

    if not selected_kingdoms:
        st.warning("Select at least one kingdom.")
        return

    filtered = df[df["kingdom"].isin(selected_kingdoms)].copy()

    eps = 0.001
    filtered["a"] = filtered["purity"] + eps
    filtered["b"] = filtered["passion"] + eps
    filtered["c"] = filtered["ignorance"] + eps

    filtered["marker_size"] = filtered["count"].apply(
        lambda n: max(4, min(40, 3 * math.log10(max(n, 1)) + 2))
    )

    fig = go.Figure()
    for kingdom in selected_kingdoms:
        kdf = filtered[filtered["kingdom"] == kingdom]
        if kdf.empty:
            continue
        fig.add_trace(go.Scatterternary(
            a=kdf["a"],
            b=kdf["b"],
            c=kdf["c"],
            mode="markers",
            name=kingdom,
            marker=dict(
                size=kdf["marker_size"],
                color=KINGDOM_COLORS.get(kingdom, "#95a5a6"),
                line=dict(width=0.5, color="white"),
                opacity=0.8,
            ),
            text=kdf.apply(
                lambda r: (
                    f"{r['class_name']}<br>"
                    f"{r['kingdom']}<br>"
                    f"Species: {r['count']:,}<br>"
                    f"Purity (Sattva): {r['purity']:.3f}<br>"
                    f"Passion (Rajas): {r['passion']:.3f}<br>"
                    f"Ignorance (Tamas): {r['ignorance']:.3f}"
                ),
                axis=1,
            ),
            hoverinfo="text",
        ))

    fig.update_layout(
        ternary=dict(
            aaxis=dict(title="Purity (Sattva)", min=0),
            baxis=dict(title="Passion (Rajas)", min=0),
            caxis=dict(title="Ignorance (Tamas)", min=0),
        ),
        height=700,
        margin=dict(t=40, b=40, l=60, r=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander("Class details", expanded=False):
        table_df = filtered[["kingdom", "class_name", "count", "purity", "passion", "ignorance"]].copy()
        table_df = table_df.sort_values("count", ascending=False)
        table_df.columns = ["Kingdom", "Class", "Species Count", "Purity", "Passion", "Ignorance"]
        table_df["Species Count"] = table_df["Species Count"].apply(lambda n: f"{n:,}")
        table_df["Purity"] = table_df["Purity"].apply(lambda v: f"{v:.3f}")
        table_df["Passion"] = table_df["Passion"].apply(lambda v: f"{v:.3f}")
        table_df["Ignorance"] = table_df["Ignorance"].apply(lambda v: f"{v:.3f}")
        st.dataframe(table_df, width="stretch", height=400)


# ── Statistics ─────────────────────────────────────────────────────────

def _render_stats() -> None:
    """Statistics tab."""
    stats = _cached_stats()
    total = stats.get("total", 0)

    if total == 0:
        st.info("No data available.")
        return

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Species Records", f"{total:,}")
    with col2:
        st.metric("Database Files", stats.get("db_file_count", 0))
    with col3:
        kingdoms = stats.get("kingdoms", {})
        st.metric("Kingdoms", len(kingdoms))

    st.divider()

    # Kingdom breakdown
    col1, col2 = st.columns(2)
    with col1:
        if kingdoms:
            colors = [KINGDOM_COLORS.get(k, "#95a5a6") for k in kingdoms.keys()]
            fig = go.Figure(data=[go.Pie(
                labels=list(kingdoms.keys()),
                values=list(kingdoms.values()),
                marker=dict(colors=colors),
                textinfo="label+percent",
                hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
            )])
            fig.update_layout(title="Species by Kingdom", height=400, margin=dict(t=40, b=20))
            st.plotly_chart(fig, width="stretch")

    with col2:
        ranks = stats.get("ranks", {})
        if ranks:
            fig = go.Figure(data=[go.Bar(
                x=list(ranks.keys()),
                y=list(ranks.values()),
                marker_color="#3498db",
                hovertemplate="%{x}: %{y:,}<extra></extra>",
            )])
            fig.update_layout(title="Records by Taxon Rank", height=400, margin=dict(t=40, b=20))
            st.plotly_chart(fig, width="stretch")

    # Top families
    top_families = stats.get("top_families", {})
    if top_families:
        fig = go.Figure(data=[go.Bar(
            y=list(top_families.keys()),
            x=list(top_families.values()),
            orientation="h",
            marker_color="#2ecc71",
            hovertemplate="%{y}: %{x:,}<extra></extra>",
        )])
        fig.update_layout(
            title="Top 20 Families by Species Count",
            height=500,
            margin=dict(t=40, b=20, l=150),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, width="stretch")

    # Taxonomic status
    statuses = stats.get("statuses", {})
    if statuses:
        cols = st.columns(len(statuses))
        for i, (status, count) in enumerate(statuses.items()):
            with cols[i % len(cols)]:
                pct = f"{count / total * 100:.1f}%"
                st.metric(status.title(), f"{count:,} ({pct})")

    # Trait scores
    trait_by_kingdom = stats.get("trait_by_kingdom", {})
    if trait_by_kingdom:
        st.divider()
        st.subheader("Trait Scores by Kingdom")
        st.caption(
            "Heuristic probabilities (0-1) based on taxonomic classification. "
            "**Mobility**: how motile the organism typically is. "
            "**Warm-blooded**: likelihood of endothermy. "
            "**Size**: typical body size on a logarithmic scale (0 = microscopic, 1 = largest organisms)."
        )

        # Overall averages
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Mobility", f"{stats.get('avg_mobility', 0):.3f}")
        with col2:
            st.metric("Avg Warm-blooded", f"{stats.get('avg_warm_blood', 0):.3f}")
        with col3:
            st.metric("Avg Size", f"{stats.get('avg_size', 0):.3f}")

        # Grouped bar chart: traits by kingdom
        kingdom_names = list(trait_by_kingdom.keys())
        mobility_vals = [trait_by_kingdom[k]["mobility"] for k in kingdom_names]
        warm_blood_vals = [trait_by_kingdom[k]["warm_blood"] for k in kingdom_names]
        size_vals = [trait_by_kingdom[k]["size"] for k in kingdom_names]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Mobility", x=kingdom_names, y=mobility_vals,
            marker_color="#3498db",
            hovertemplate="%{x}: %{y:.3f}<extra>Mobility</extra>",
        ))
        fig.add_trace(go.Bar(
            name="Warm-blooded", x=kingdom_names, y=warm_blood_vals,
            marker_color="#e74c3c",
            hovertemplate="%{x}: %{y:.3f}<extra>Warm-blooded</extra>",
        ))
        fig.add_trace(go.Bar(
            name="Size", x=kingdom_names, y=size_vals,
            marker_color="#2ecc71",
            hovertemplate="%{x}: %{y:.3f}<extra>Size</extra>",
        ))
        fig.update_layout(
            title="Average Trait Scores by Kingdom",
            barmode="group",
            yaxis=dict(title="Score (0-1)", range=[0, 1]),
            height=450,
            margin=dict(t=40, b=20),
        )
        st.plotly_chart(fig, width="stretch")

        # Radar chart per kingdom
        col1, col2 = st.columns(2)
        with col1:
            fig_radar = go.Figure()
            for k in kingdom_names:
                vals = trait_by_kingdom[k]
                fig_radar.add_trace(go.Scatterpolar(
                    r=[vals["mobility"], vals["warm_blood"], vals["size"], vals["mobility"]],
                    theta=["Mobility", "Warm-blooded", "Size", "Mobility"],
                    name=k,
                    line_color=KINGDOM_COLORS.get(k, "#95a5a6"),
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title="Trait Profiles by Kingdom",
                height=450,
                margin=dict(t=40, b=20),
            )
            st.plotly_chart(fig_radar, width="stretch")

        with col2:
            # Table view
            trait_data = []
            for k in kingdom_names:
                vals = trait_by_kingdom[k]
                trait_data.append({
                    "Kingdom": k,
                    "Species Count": f"{int(vals['count']):,}",
                    "Mobility": f"{vals['mobility']:.3f}",
                    "Warm-blooded": f"{vals['warm_blood']:.3f}",
                    "Size": f"{vals['size']:.3f}",
                })
            st.dataframe(pd.DataFrame(trait_data), width="stretch", height=380)


# ── Shared display helpers ─────────────────────────────────────────────

DISPLAY_COLUMNS = [
    "scientific_name", "canonical_name", "kingdom", "phylum",
    "class_name", "order_name", "family", "genus",
    "taxon_rank", "taxonomic_status",
    "mobility_score", "warm_blood_score", "size_score",
]

COLUMN_LABELS = {
    "scientific_name": "Scientific Name",
    "canonical_name": "Canonical Name",
    "kingdom": "Kingdom",
    "phylum": "Phylum",
    "class_name": "Class",
    "order_name": "Order",
    "family": "Family",
    "genus": "Genus",
    "taxon_rank": "Rank",
    "taxonomic_status": "Status",
    "mobility_score": "Mobility",
    "warm_blood_score": "Warm-blooded",
    "size_score": "Size",
}


def _display_species_table(records: list[dict], key_prefix: str = "species") -> None:
    """Display species records as a styled dataframe."""
    df = pd.DataFrame(records)
    available = [c for c in DISPLAY_COLUMNS if c in df.columns]
    display_df = df[available].rename(columns=COLUMN_LABELS)

    st.dataframe(
        display_df,
        width="stretch",
        height=min(600, 40 + len(records) * 35),
    )

    # CSV export
    csv_data = display_df.to_csv(index=False)
    st.download_button(
        "Export as CSV", csv_data, "species_results.csv", "text/csv",
        key=f"{key_prefix}_csv_export",
    )
