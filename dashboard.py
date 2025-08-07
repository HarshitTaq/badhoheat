import pandas as pd
import plotly.express as px

# Step 1: Upload your file
uploaded_file = 'your_file.csv'  # Replace with actual filename

# Step 2: Read only first two columns (district and count)
df = pd.read_csv(uploaded_file, usecols=[0, 1], encoding='utf-8')

# Step 3: Rename columns to standard names
df.columns = ['district', 'count']

# Step 4: Drop rows where count is missing or zero
df.dropna(subset=['district', 'count'], inplace=True)
df = df[df['count'] > 0]

# Step 5: Map district to state
def get_state_from_district(district):
    mapping = {
        'Adilabad': 'Telangana',
        'Agar Malwa': 'Madhya Pradesh',
        'Agra': 'Uttar Pradesh',
        'Ahmedabad': 'Gujarat',
        # Add all other mappings here
    }
    return mapping.get(district.strip(), 'Unknown')

df['state'] = df['district'].apply(get_state_from_district)

# Step 6: Group by state and sum
state_data = df.groupby('state')['count'].sum().reset_index()

# Step 7: Sort descending
state_data.sort_values(by='count', ascending=False, inplace=True)

# Step 8: Plot heatmap using Plotly
fig = px.bar(
    state_data,
    y='state',
    x='count',
    orientation='h',
    color='count',
    color_continuous_scale='YlOrRd',
    title='Heat Map of Notifications Received by State'
)

fig.update_layout(
    xaxis_title='Notification Count',
    yaxis_title='State',
    coloraxis_colorbar=dict(title='Count'),
    height=800
)

fig.show()
