import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="State Notification Heatmap", page_icon="🗺️")
st.title("🗺️ Heat Map of Notifications by State")

# Upload section
uploaded_file = st.file_uploader("📤 Upload your district-wise CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Step 1: Read only first two columns; skip the header row if it's junk
        df = pd.read_csv(uploaded_file, usecols=[0, 1], skiprows=1, header=None)
        df.columns = ['district', 'count']

        # Step 2: Clean the data
        df.dropna(subset=['district', 'count'], inplace=True)
        df = df[df['count'] > 0]

        # Step 3: Map district to state
        def get_state_from_district(district):
            mapping = {
                'Adilabad': 'Telangana',
                'Agar Malwa': 'Madhya Pradesh',
                'Agra': 'Uttar Pradesh',
                'Ahmedabad': 'Gujarat',
                # Add full mappings here
            }
            return mapping.get(district.strip(), 'Unknown')

        df['state'] = df['district'].apply(get_state_from_district)

        # Step 4: Group and sort
        state_data = df.groupby('state')['count'].sum().reset_index()
        state_data.sort_values(by='count', ascending=False, inplace=True)

        # Step 5: Plot the heatmap
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

    except Exception as e:
        st.error(f"❌ Error while processing file: {e}")
else:
    st.info("📎 Please upload a CSV file with district-wise notification counts.")
