import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="State Notification Heatmap", page_icon="🗺️")
st.title("📊 Heat Map of Notifications by State")

st.markdown("""
Welcome to the Notification Dashboard!  
📤 Please upload a file containing **district-wise notification counts**.

- Supported formats: `.csv` and `.xlsx`  
- First column = District name  
- Second column = Notification count  
- Header row (if any) will be ignored
""")

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if not uploaded_file:
    st.warning("⏳ Waiting for a file to be uploaded...")
    st.stop()

try:
    # Handle CSV or Excel file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, header=None)
    else:
        st.error("Unsupported file type.")
        st.stop()

    # Skip header row and take first two columns
    df = df.iloc[1:, [0, 1]]
    df.columns = ['district', 'count']

    # Convert and clean
    df['count'] = pd.to_numeric(df['count'], errors='coerce')
    df.dropna(subset=['district', 'count'], inplace=True)
    df = df[df['count'] > 0]

    # Sample district → state mapping
    def get_state_from_district(district):
        mapping = {
            'Adilabad': 'Telangana',
            'Agra': 'Uttar Pradesh',
            'Ahmedabad': 'Gujarat',
            'Agar Malwa': 'Madhya Pradesh',
            # Extend this mapping...
        }
        return mapping.get(str(district).strip(), 'Unknown')

    df['state'] = df['district'].apply(get_state_from_district)

    # Group and sort
    state_data = df.groupby('state')['count'].sum().reset_index()
    state_data.sort_values(by='count', ascending=False, inplace=True)

    # Plot
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
