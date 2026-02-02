import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Grandiose Audit Dashboard")

uploaded_file = st.file_uploader("Upload your audit data file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Deduplicate by submission_id + question
    if 'submission_id' in df.columns and 'question' in df.columns:
        question_df = df.groupby(['submission_id', 'question']).agg({
            'risk': 'first',
            'observation': 'first',
            'store': 'first'
        }).reset_index()
    else:
        st.error("Required columns missing: submission_id and question")
        st.stop()

    # --- KPI Metrics ---
    st.subheader("Key Metrics")

    # Risks side by side
    col1, col2, col3 = st.columns(3)
    col1.metric("High Risks", (question_df['risk'] == "High Risk").sum())
    col2.metric("Medium Risks", (question_df['risk'] == "Medium Risk").sum())
    col3.metric("Low Risks", (question_df['risk'] == "Low Risk").sum())

    # Observations side by side
    col4, col5 = st.columns(2)
    col4.metric("New Observations", (question_df['observation'] == "New").sum())
    col5.metric("Repeated Observations", (question_df['observation'] == "Repeated").sum())

    # --- Risk Distribution ---
    st.subheader("Risk Distribution")
    risk_order = ["High Risk", "Medium Risk", "Low Risk"]
    risk_counts = question_df['risk'].value_counts().reindex(risk_order, fill_value=0)

    fig, ax = plt.subplots()
    colors = ["red", "yellow", "green"]
    ax.bar(risk_counts.index, risk_counts.values, color=colors)
    ax.set_ylabel("Count")
    ax.set_title("Risk Distribution (High → Medium → Low)")
    st.pyplot(fig)

    # --- Observation Distribution ---
    st.subheader("Observation Distribution")
    obs_counts = question_df['observation'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(obs_counts, labels=obs_counts.index, autopct='%1.1f%%')
    ax1.set_title("Observation Distribution")
    st.pyplot(fig1)

    # --- Observation by Question ---
    st.subheader("Observation Distribution by Question")
    obs_by_question = question_df.groupby(['question', 'observation']).size().unstack(fill_value=0)
    st.dataframe(obs_by_question)

    # --- Observation by Store ---
    st.subheader("Observation Distribution by Store")
    store_filter = st.selectbox("Filter by Store", options=["All"] + list(question_df['store'].dropna().unique()))
    if store_filter != "All":
        filtered_df = question_df[question_df['store'] == store_filter]
    else:
        filtered_df = question_df

    obs_by_store = filtered_df.groupby(['store', 'observation']).size().unstack(fill_value=0)
    st.dataframe(obs_by_store)

    # --- Team Impacted by Questions ---
    st.subheader("Team Impacted by Questions")
    if 'team_impacted' in df.columns:
        team_question_df = df[['submission_id', 'question', 'team_impacted']].drop_duplicates()
        team_question_df['team_impacted'] = team_question_df['team_impacted'].astype(str).str.split(',')
        exploded = team_question_df.explode('team_impacted')
        exploded['team_impacted'] = exploded['team_impacted'].str.strip()
        team_counts = exploded.groupby('team_impacted')['question'].nunique().sort_values(ascending=False)
        fig2, ax2 = plt.subplots()
        team_counts.plot(kind="bar", ax=ax2)
        ax2.set_title("Team Impacted by Questions (Descending Order)")
        st.pyplot(fig2)

    st.success("Dashboard generated successfully with updated layout and logic!")
