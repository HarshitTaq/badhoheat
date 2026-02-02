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
            'store': 'first',
            'team_impacted': 'first'
        }).reset_index()
    else:
        st.error("Required columns missing: submission_id and question")
        st.stop()

    # --- KPI Metrics ---
    st.subheader("Key Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("High Risks", (question_df['risk'] == "High Risk").sum())
    col2.metric("Medium Risks", (question_df['risk'] == "Medium Risk").sum())
    col3.metric("Low Risks", (question_df['risk'] == "Low Risk").sum())

    col4, col5 = st.columns(2)
    col4.metric("New Observations", (question_df['observation'] == "New").sum())
    col5.metric("Repeated Observations", (question_df['observation'] == "Repeated").sum())

    # --- 1) Risk Distribution ---
    st.subheader("Risk Distribution")
    risk_order = ["High Risk", "Medium Risk", "Low Risk"]
    risk_counts = question_df['risk'].value_counts().reindex(risk_order, fill_value=0)

    fig, ax = plt.subplots()
    colors = ["red", "#FFBF00", "green"]  # Red, Amber, Green
    ax.bar(risk_counts.index, risk_counts.values, color=colors)
    ax.set_ylabel("Count")
    ax.set_title("Risk Distribution (High → Medium → Low)")
    st.pyplot(fig)
    st.dataframe(risk_counts.rename("Count"))

    # --- 2) Heatmap: Risk vs Team Impacted ---
    st.subheader("Heatmap: Risk vs Team Impacted")
    df['team_impacted'] = df['team_impacted'].astype(str).apply(
        lambda x: x.split(',') if ',' in x else [x]
    )
    exploded_risk = df.explode('team_impacted')
    exploded_risk['team_impacted'] = exploded_risk['team_impacted'].str.strip()
    heatmap_data = exploded_risk.groupby(['team_impacted', 'risk']).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(columns=["High Risk", "Medium Risk", "Low Risk"], fill_value=0)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Blues", ax=ax2)
    ax2.set_title("Heatmap: Risk vs Team Impacted")
    st.pyplot(fig2)
    st.dataframe(heatmap_data)

    # --- 3) Observation Distribution ---
    st.subheader("Observation Distribution")
    obs_counts = question_df['observation'].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(obs_counts, labels=obs_counts.index, colors=["#1f77b4", "orange"], autopct='%1.1f%%')
    ax3.set_title("Observation Distribution")
    st.pyplot(fig3)
    st.dataframe(obs_counts.rename("Count"))

    # --- 4) Observation by Question ---
    st.subheader("Observation Distribution by Question")
    obs_by_question = question_df.groupby(['question', 'observation']).size().unstack(fill_value=0)
    if 'New' in obs_by_question.columns:
        obs_by_question = obs_by_question.sort_values(by='New', ascending=False)

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    obs_by_question.plot(kind='bar', stacked=True, color=["#1f77b4", "orange"], ax=ax4)
    ax4.set_title("Observation by Question (Sorted by New)")
    ax4.set_ylabel("Count")
    st.pyplot(fig4)
    st.dataframe(obs_by_question)

    # --- 5) Observation by Store ---
    st.subheader("Observation Distribution by Store")
    store_filter = st.selectbox("Filter by Store", options=["All"] + list(question_df['store'].dropna().unique()))
    if store_filter != "All":
        filtered_df_store = question_df[question_df['store'] == store_filter]
    else:
        filtered_df_store = question_df

    obs_by_store = filtered_df_store.groupby(['store', 'observation']).size().unstack(fill_value=0)
    if 'New' in obs_by_store.columns:
        obs_by_store = obs_by_store.sort_values(by='New', ascending=False)

    fig5, ax5 = plt.subplots(figsize=(8, 4))
    obs_by_store.plot(kind='bar', stacked=True, color=["#1f77b4", "orange"], ax=ax5)
    ax5.set_title("Observation by Store (Sorted by New)")
    ax5.set_ylabel("Count")
    st.pyplot(fig5)
    st.dataframe(obs_by_store)

    # --- 6) Teams Impacted (Distinct Count) ---
    st.subheader("Teams Impacted")

    # Filter by Question
    question_filter = st.selectbox("Filter by Question", options=["All"] + list(df['question'].dropna().unique()))
    if question_filter != "All":
        filtered_df_team = df[df['question'] == question_filter]
    else:
        filtered_df_team = df

    # Split into multiple rows (only split if comma exists)
    filtered_df_team['team_impacted'] = filtered_df_team['team_impacted'].astype(str).apply(
        lambda x: x.split(',') if ',' in x else [x]
    )
    exploded = filtered_df_team.explode('team_impacted')
    exploded['team_impacted'] = exploded['team_impacted'].str.strip()

    # Simple distinct count
    team_counts = exploded['team_impacted'].value_counts()

    # Plot
    fig6, ax6 = plt.subplots()
    team_counts.plot(kind="bar", color="#1f77b4", ax=ax6)
    ax6.set_title("Teams Impacted (Distinct Count)")
    ax6.set_ylabel("Count")
    st.pyplot(fig6)

    # Grid at bottom
    st.dataframe(team_counts.rename("Distinct Count"))
