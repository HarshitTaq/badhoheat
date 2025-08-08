import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Notification Heatmap", page_icon="🗺️")
st.title("📊 Heat Map")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if not uploaded_file:
    st.info("Please upload a file")
    st.stop()

# Read first two columns, skip header row
if uploaded_file.name.lower().endswith(".csv"):
    raw = pd.read_csv(uploaded_file, header=None)
else:
    raw = pd.read_excel(uploaded_file, header=None)

df = raw.iloc[1:, [0, 1]].copy()
df.columns = ["label", "value"]

# Clean
df["label"] = df["label"].astype(str).str.strip()
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["label", "value"])
df = df[df["value"] > 0]

# Group and sort
agg = df.groupby("label", as_index=False)["value"].sum()
agg = agg.sort_values("value", ascending=False)

# Auto height
bar_height = min(max(agg.shape[0] * 26, 500), 3800)

# Prepare heatmap values
z = np.array(agg["value"], dtype=float).reshape(-1, 1)
y_labels = agg["label"].tolist()

fig = go.Figure(
    data=go.Heatmap(
        z=z,
        x=["Count"],  # single centered column
        y=y_labels,
        colorscale="YlOrRd",
        colorbar=dict(title="Count"),
        showscale=True
    )
)

# Add text annotations
for i, val in enumerate(agg["value"]):
    fig.add_annotation(
        x="Count", y=y_labels[i],
        text=str(int(val)) if float(val).is_integer() else f"{val}",
        showarrow=False, font=dict(size=12, color="black")
    )

fig.update_layout(
    title="Heat Map of Notifications Received",
    xaxis_title="", yaxis_title="",
    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(autorange="reversed"),
    height=bar_height,
    margin=dict(l=150, r=40, t=60, b=20)
)

st.plotly_chart(fig, use_container_width=True)
