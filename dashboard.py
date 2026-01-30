import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Grandiose Audit Dashboard")

uploaded_file = st.file_uploader("Upload your audit data file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load and clean data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Check required columns
    required_cols = ['submission_id', 'question', 'risk', 'observation', 'team_impacted']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
    else:
        # Deduplicate by submission_id + question
        question_df = df.groupby(['submission_id', 'question']).agg({
            'risk': 'first',
            'observation': 'first'
        }).reset_index()

        # --- KPI Metrics ---
        st.subheader("Key Metrics")
        total_questions = question_df.shape[0]
        high_risk = (question_df['risk'] == "High Risk").sum()
        medium_risk = (question_df['risk'] == "Medium Risk").sum()
        low_risk = (question_df['risk'] == "Low Risk").sum()
        new_obs = (question_df['observation'] == "New").sum()
        repeated_obs = (question_df['observation'] == "Repeated").sum()

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
        st.bar_chart(question_df['risk'].value_counts())

        # --- Observation Distribution ---
        st.subheader("Observation Distribution")
        obs_counts = question_df['observation'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(obs_counts, labels=obs_counts.index, autopct='%1.1f%%')
        ax1.set_title("Observation Distribution")
        st.pyplot(fig1)

        # --- Team Impacted Breakdown ---
        st.subheader("Team Impacted by Questions")
        team_question_df = df[['submission_id', 'question', 'team_impacted']].drop_duplicates()
        team_question_df['team_impacted'] = team_question_df['team_impacted'].astype(str).str.split(',')

        exploded = team_question_df.explode('team_impacted')
        exploded['team_impacted'] = exploded['team_impacted'].str.strip()
        team_counts = exploded.groupby('team_impacted')['question'].nunique().sort_values(ascending=False)
        st.bar_chart(team_counts)

        # --- Heatmap: Risk vs Team Impacted ---
        st.subheader("Heatmap: Risk vs Team Impacted")
        df['team_impacted'] = df['team_impacted'].astype(str).str.split(',')
        exploded_risk = df.explode('team_impacted')
        exploded_risk['team_impacted'] = exploded_risk['team_impacted'].str.strip()
        heatmap_data = exploded_risk.groupby(['team_impacted', 'risk']).size().unstack(fill_value=0)
        fig2, ax2 = plt.subplots(figsize=(10,6))
        sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Blues", ax=ax2)
        st.pyplot(fig2)

        st.success("Dashboard generated successfully with corrected logic!")
