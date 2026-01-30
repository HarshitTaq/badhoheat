import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Dashboard Title
st.title("Grandiose Audit Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your audit data file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # --- Deduplicate by Submission Id ---
    dedup_df = df.groupby('Submission Id').agg({
        'Risk': 'first',
        'Observation': 'first'
    }).reset_index()

    # --- KPI Metrics ---
    st.subheader("Key Metrics")
    total_submissions = dedup_df['Submission Id'].nunique()
    high_risk = (dedup_df['Risk'] == "High Risk").sum()
    medium_risk = (dedup_df['Risk'] == "Medium Risk").sum()
    low_risk = (dedup_df['Risk'] == "Low Risk").sum()
    new_obs = (dedup_df['Observation'] == "New").sum()
    repeated_obs = (dedup_df['Observation'] == "Repeated").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Submissions", total_submissions)
    col2.metric("High Risks", high_risk)
    col3.metric("Medium Risks", medium_risk)

    col4, col5, col6 = st.columns(3)
    col4.metric("Low Risks", low_risk)
    col5.metric("New Observations", new_obs)
    col6.metric("Repeated Observations", repeated_obs)

    # --- Risk Distribution ---
    st.subheader("Risk Distribution")
    risk_counts = dedup_df['Risk'].value_counts()
    st.bar_chart(risk_counts)

    # --- Risks by Team Impacted ---
    st.subheader("Risks by Team Impacted")
    risks_by_team = df.groupby(['Team Impacted', 'Risk']).size().unstack(fill_value=0)
    st.dataframe(risks_by_team)
    st.bar_chart(risks_by_team)

    # --- Observation Distribution ---
    st.subheader("Observation Distribution")
    obs_counts = dedup_df['Observation'].value_counts()
    obs_counts_numeric = obs_counts.astype(float)
    st.pyplot(plt.figure(figsize=(5,5)))
    plt.pie(obs_counts_numeric, labels=obs_counts_numeric.index, autopct='%1.1f%%')
    plt.title("Observation Distribution")
    st.pyplot(plt)

    # --- Observations by Team Impacted ---
    st.subheader("Observations by Team Impacted")
    obs_by_team = df.groupby(['Team Impacted', 'Observation']).size().unstack(fill_value=0)
    st.dataframe(obs_by_team)
    st.bar_chart(obs_by_team)

    # --- Heatmap of Risks vs Teams ---
    st.subheader("Heatmap: Risks vs Teams")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.heatmap(risks_by_team, annot=True, fmt="d", cmap="Blues", ax=ax)
    st.pyplot(fig)

    # --- Line Chart: Risk Trend over Time ---
    st.subheader("Risk Trend Over Time")
    if 'Started At' in df.columns:
        df['Started At'] = pd.to_datetime(df['Started At'], errors='coerce')
        risk_trend = df.groupby([df['Started At'].dt.date, 'Risk']).size().unstack(fill_value=0)
        st.line_chart(risk_trend)

    st.success("Dashboard generated successfully for Grandiose!")
