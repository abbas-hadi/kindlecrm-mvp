import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="KindleCRM.ai MVP", layout="wide")
st.title("KindleCRM.ai — Donor Data Upload & Insights")

uploaded_file = st.file_uploader("Upload your donor CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Raw Donor Data")
    st.dataframe(df)

    # Basic sanity check for expected columns
    expected_cols = {"name", "email", "donation_date", "donation_amount"}
    if not expected_cols.issubset(set(df.columns.str.lower())):
        st.error(f"CSV missing required columns: {expected_cols}")
    else:
        # Normalize columns
        df.columns = df.columns.str.lower()
        
        # Parse dates
        df["donation_date"] = pd.to_datetime(df["donation_date"], errors="coerce")
        
        # Aggregate donor stats
        donor_stats = df.groupby(["name", "email"]).agg(
            total_donated=pd.NamedAgg(column="donation_amount", aggfunc="sum"),
            last_donation=pd.NamedAgg(column="donation_date", aggfunc="max"),
            donation_count=pd.NamedAgg(column="donation_amount", aggfunc="count"),
        ).reset_index()

        st.subheader("Donor Profiles & Summary")
        st.dataframe(donor_stats)

        # Select donor for detailed view
        donor_name = st.selectbox("Select a donor to view details", donor_stats["name"].unique())

        if donor_name:
            donor_data = df[df["name"] == donor_name].sort_values("donation_date", ascending=False)
            st.write(f"### Donation History for {donor_name}")
            st.dataframe(donor_data[["donation_date", "donation_amount"]])
