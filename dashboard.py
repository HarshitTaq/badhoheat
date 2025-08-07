import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="State Notification Heatmap", page_icon="🗺️")
st.title("🗺️ Heat Map of Notifications by State")

# Upload section
uploaded_file = st.file_uploader("📤 Upload your district-wise CSV file", type=["csv"])

if uploaded_file:
    # Read file, assuming the first row is header but names might be wrong — we don't care
    df = pd.read_csv(uploaded_file, usecols=[0, 1], skiprows=1, header=None)
    df.columns = ['district', 'count']  # Rename to standard names

    # Clean and filter
    df.dropna(subset=['district', 'count'], inplace=True)
    df = df[df['count'] > 0]

    # Map district to state
    def get_state_from_district(district):
        mapping = {
            'Adilabad': 'Telangana',
            'Agar Malwa': 'Madhya Pradesh',
            'Agra': 'Uttar Pradesh',
            'Ahmedabad': 'Gujarat',
            # Add the full mapping based on your CSV here
        }
        return mapping.get(district.strip(), 'Unknown')

    df['state'] = df['district'].apply(get_state_from_district)

    # Group by state
    state_data = df.groupby('state')['count'].sum().reset_index()
    state_data.sort_values(by='count', ascending=False, inplace=True)

    # Plot heatmap
    fig = px.bar(
        state_data,
        y='state',
        x='count',
        orientation='h',
        color='count',
        color_continuous_scale='YlOrRd',
        title='Heat Map of Notifications Received by State'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Heatmap generated successfully!")

else:
    st.info("📎 Please upload a CSV file with district-wise notification counts.")
