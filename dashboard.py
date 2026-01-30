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

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Clean Team Impacted if it's comma-separated
    df['Team Impacted'] = df['Team Impacted'].astype(str)

    # Deduplicate by Submission Id + Question
    question_df = df.groupby(['Submission Id', 'Question']).agg({
        'Risk': 'first',
        'Observation': 'first'
    }).reset_index()

    # --- KPI Metrics ---
    st.subheader("Key Metrics")
    total_questions = question_df.shape[0]
    high_risk = (question_df['Risk'] == "High Risk").sum()
    medium_risk = (question_df['Risk'] == "Medium Risk").sum()
    low_risk = (question_df['Risk'] == "Low Risk").sum()
    new_obs = (question_df['Observation'] == "New").sum()
    repeated_obs = (question_df['Observation'] == "Repeated").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", total_questions)
    col2.metric("High Risks", high_risk)
    col3.metric("Medium Risks", medium_risk)

    col4, col5, col6 = st.columns(3)
    col4.metric("Low Risks", low_risk)
    col5.metric("New Observations", new_obs)
    col6.metric("Repeated Observations", repeated_obs)

    # --- Risk Distribution ---
    st.subheader("Risk Distribution")
    risk_counts = question_df['Risk'].value_counts()
    st.bar_chart(risk_counts)

    # --- Observation Distribution ---
    st.subheader("Observation Distribution")
    obs_counts = question_df['Observation'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(obs_counts, labels=obs_counts.index, autopct='%1.1f%%')
    ax1.set_title("Observation Distribution")
    st.pyplot(fig1)

    # --- Team Impacted Breakdown ---
    st.subheader("Team Impacted by Questions")
    team_question_df = df[['Submission Id', 'Question', 'Team Impacted']].drop_duplicates()
    team_question_df['Team Impacted'] = team_question_df['Team Impacted'].str.split(',')

    exploded = team_question_df.explode('Team Impacted')
    exploded['Team Impacted'] = exploded['Team Impacted'].str.strip()
    team_counts = exploded.groupby('Team Impacted')['Question'].nunique().sort_values(ascending=False)
    st.bar_chart(team_counts)

    # --- Heatmap: Risk vs Team Impacted ---
    st.subheader("Heatmap: Risk vs Team Impacted")
    df['Team Impacted'] = df['Team Impacted'].str.split(',')
    exploded_risk = df.explode('Team Impacted')
    exploded_risk['Team Impacted'] = exploded_risk['Team Impacted'].str.strip()
    heatmap_data = exploded_risk.groupby(['Team Impacted', 'Risk']).size().unstack(fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(10,6))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Blues", ax=ax2)
    st.pyplot(fig2)

    st.success("Dashboard generated successfully with corrected logic!")
