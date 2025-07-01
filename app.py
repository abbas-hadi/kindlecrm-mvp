import streamlit as st
import pandas as pd
from datetime import datetime
import openai

# Load OpenAI API key securely from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="KindleCRM.ai MVP", layout="wide")
st.title("KindleCRM.ai — Donor Data Upload & Insights")

def generate_email(donor_name, total_donated, message_type, context):
    system_prompt = "You are a warm, professional fundraising officer writing personalized donor emails."
    
    prompt = f"""
Write a {message_type} email to {donor_name}, who has donated a total of ${total_donated}.
Tone: Appreciative, personal, mission-driven.
Context: {context or "none"}
Keep it short (3–5 sentences), friendly, and donor-centric.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response["choices"][0]["message"]["content"].strip()

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

            # --- GPT Email Generator UI ---
            st.subheader("🎯 GPT Email Assistant")

            donor_row = donor_stats[donor_stats["name"] == donor_name].iloc[0]
            total_donated = donor_row["total_donated"]

            message_type = st.selectbox(
                "Select message type",
                ["Thank You", "Donation Appeal", "Renewal Ask"]
            )

            context = st.text_area("Add optional campaign context or message notes")

            if st.button("Generate Email with GPT"):
                with st.spinner("Writing email..."):
                    email_text = generate_email(
                        donor_name,
                        total_donated,
                        message_type,
                        context
                    )
                    st.success("✅ Email generated!")
                    st.text_area("Generated Email", email_text, height=200)

        

    

        
