import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Notification Heatmap", page_icon="🗺️")
st.title("📊 Heat Map")

st.markdown("""
Upload a `.csv` or `.xlsx` with **two columns of data**:
- First column: text labels (any names)
- Second column: numeric values

Headers (if any) are ignored. Only the **first two columns** are used.
""")

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if not uploaded_file:
    st.info("Waiting for a file…")
    st.stop()

# ---- READ FILE (first two cols, ignore header row) ----
if uploaded_file.name.lower().endswith(".csv"):
    raw = pd.read_csv(uploaded_file, header=None)
else:
    raw = pd.read_excel(uploaded_file, header=None)

# take only first two columns; skip the first row (assumed header-ish)
df = raw.iloc[1:, [0, 1]].copy()
df.columns = ["label", "value"]  # neutral names

# clean
df["label"] = df["label"].astype(str).str.strip()
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["label", "value"])
df = df[df["value"] > 0]

# group by whatever is in col 1, sum values
agg = df.groupby("label", as_index=False)["value"].sum()

# sort by value desc
agg = agg.sort_values("value", ascending=False)

# dynamic height so long lists fit (cap height to avoid going absurd)
bar_height = min(max(agg.shape[0] * 22, 400), 3500)

fig = px.bar(
    agg,
    y="label",
    x="value",
    orientation="h",
    color="value",
    color_continuous_scale="YlOrRd",
    title="Notifications (by first-column labels)"
)
fig.update_layout(
    xaxis_title="count",
    yaxis_title="",
    height=bar_height,
    coloraxis_colorbar=dict(title="count"),
    margin=dict(l=10, r=10, t=60, b=10)
)

st.plotly_chart(fig, use_container_width=True)
st.success("✅ Heatmap generated.")
