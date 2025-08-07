import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="State Notification Heatmap", page_icon="🗺️")
st.title("📊 Heat Map of Notifications by State")

st.markdown("""
Welcome to the Notification Dashboard!  
📤 Please upload a CSV file containing **district-wise notification counts** using the uploader below.

- The **first column** should have district names  
- The **second column** should have corresponding counts  
- The header row (if any) will be ignored
""")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# If no file is uploaded yet
if not uploaded_file:
    st.warning("⏳ Waiting for a file to be uploaded...")
    st.stop()

# Once file is uploaded, process and display the dashboard
try:
    # Read file with no header, skip first row (header), take first 2 columns only
    df = pd.read_csv(uploaded_file, header=None)
    df = df.iloc[1:, [0, 1]]
    df.columns = ['district', 'count']

    # Convert counts to numeric, filter clean data
    df['count'] = pd.to_numeric(df['count'], errors='coerce')
    df.dropna(subset=['district', 'count'], inplace=True)
    df = df[df['count'] > 0]

    # Dummy mapping - extend with full district → state mapping
    def get_state_from_district(district):
        mapping = {
            'Adilabad': 'Telangana',
            'Agra': 'Uttar Pradesh',
            'Ahmedabad': 'Gujarat',
            'Agar Malwa': 'Madhya Pradesh',
            # Add more...
        }
        return mapping.get(district.strip(), 'Unknown')

    df['state'] = df['district'].apply(get_state_from_district)

    # Group and sort
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
        title='Notifications Received by State'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Heatmap generated successfully!")

except Exception as e:
    st.error(f"❌ Error processing the file: {e}")
