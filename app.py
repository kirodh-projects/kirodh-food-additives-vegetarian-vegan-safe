import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from data_downloader import ensure_data

# -------------------------------------------------
# Setup
# -------------------------------------------------
load_dotenv()
# ensure_data()

DATA_DIR = os.getenv("DATA_DIR", "./data")
E_DATA_URL = os.getenv("E_DATA_URL")

# e_df = pd.read_csv(f"{DATA_DIR}/additives.csv")
e_df = pd.read_csv(f"{DATA_DIR}/{E_DATA_URL}")
# ins_df = pd.read_csv(f"{DATA_DIR}/ins_numbers.csv")

# Normalize columns defensively
e_df.columns = e_df.columns.str.lower()
# ins_df.columns = ins_df.columns.str.lower()

# -------------------------------------------------
# UI
# -------------------------------------------------
st.set_page_config(page_title="Food Additive Lookup", layout="centered")

st.title("🍽️ Food Additive Lookup")
st.caption("INS & E-Number Additive Database")

system = st.radio(
    "Select numbering system:",
    ["E Number"], #, "INS Number"],
    horizontal=True
)

input_code = st.text_input(
    "Enter additive number (example: 102, 621):",
    max_chars=6
)

if st.button("Search", type="primary"):
    if not input_code.strip():
        st.warning("Please enter a number.")
    else:
        df = e_df # if system == "E Number" else ins_df

        result = df[df["e_code"].astype(str) == "E"+input_code.strip()]
        # print("e"+input_code.strip().lower())
        # print(df["e_code"].astype(str))

        if result.empty:
            st.error("No additive found.")
        else:
            row = result.iloc[0]

            st.subheader(f"{system}: {row['e_code']}")
            st.write(f"**Title:** {row.get('title', 'N/A')}")
            st.write(f"**Info:** {row.get('info', 'N/A')}")
            st.write(f"**E type:** {row.get('e_type', 'N/A')}")
            st.write(f"**Halal Status:** {row.get('halal_status', 'N/A')}")

# -------------------------------------------------
# Optional: Data overview
# -------------------------------------------------
with st.expander("📊 Browse additive list"):
    st.dataframe(
        e_df, #if system == "E Number" else ins_df,
        use_container_width=True,
        height=300
    )
