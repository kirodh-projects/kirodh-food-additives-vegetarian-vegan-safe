"""Display component for a single food additive."""

import streamlit as st

STATUS_COLORS = {
    "Yes": ":green[Yes]",
    "No": ":red[No]",
    "Maybe": ":orange[Maybe]",
    "Unknown": ":gray[Unknown]",
    "Halal": ":green[Halal]",
    "Doubtful": ":orange[Doubtful]",
    "Haram": ":red[Haram]",
    "Safe": ":green[Safe]",
    "Caution": ":orange[Caution]",
    "Avoid": ":red[Avoid]",
    "Banned": ":red[Banned]",
}


def _colored(value: str) -> str:
    return STATUS_COLORS.get(value, f":gray[{value}]")


def render_additive_card(additive: dict) -> None:
    """Render a detailed card for a single additive."""
    e_num = additive.get("e_number", "N/A")
    ins_num = additive.get("ins_number", "")
    title = additive.get("common_name", "Unknown")

    header = f"**{e_num}** - {title}"
    if ins_num:
        header += f" (INS {ins_num})"

    st.subheader(header)

    # Status pills row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Vegan:** {_colored(additive.get('vegan_status', 'Unknown'))}")
    with col2:
        st.markdown(f"**Vegetarian:** {_colored(additive.get('vegetarian_status', 'Unknown'))}")
    with col3:
        st.markdown(f"**Halal:** {_colored(additive.get('halal_status', 'Unknown'))}")
    with col4:
        st.markdown(f"**Safety:** {_colored(additive.get('safety_level', 'Unknown'))}")

    # Details row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Category:** {additive.get('category', 'Unknown')}")
    with col2:
        st.markdown(f"**Origin:** {additive.get('origin', 'Unknown')}")
    with col3:
        if additive.get("adi"):
            st.markdown(f"**ADI:** {additive['adi']}")

    # Chemical name
    chem = additive.get("chemical_name", "")
    alt = additive.get("alternative_names", "")
    if chem:
        st.markdown(f"**Chemical name:** {chem}")
    if alt:
        st.markdown(f"**Also known as:** {alt}")

    # Approval badges
    approvals = []
    if additive.get("approval_eu"):
        approvals.append("EU")
    if additive.get("approval_us"):
        approvals.append("US")
    if additive.get("approval_codex"):
        approvals.append("Codex")
    if approvals:
        st.markdown(f"**Approved in:** {', '.join(approvals)}")
    if additive.get("is_banned_anywhere"):
        st.markdown(":red[**Banned in some jurisdictions**]")

    # Description
    desc = additive.get("description", "")
    if desc and len(desc) > 30:
        with st.expander("Full description"):
            st.write(desc)

    st.divider()
