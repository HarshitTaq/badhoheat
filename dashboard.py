import numpy as np
import plotly.graph_objects as go

# agg must already be: label | value, sorted desc
bar_height = min(max(agg.shape[0] * 26, 500), 3800)

# 1-column heatmap (centered), values descending (top = max)
z = np.array(agg["value"], dtype=float).reshape(-1, 1)
y_labels = agg["label"].tolist()

fig = go.Figure(
    data=go.Heatmap(
        z=z,
        x=["Count"],                # single centered column
        y=y_labels,
        colorscale="YlOrRd",
        colorbar=dict(title="Count"),
        showscale=True
    )
)

# add value labels inside the cells
for i, val in enumerate(agg["value"]):
    fig.add_annotation(
        x="Count", y=y_labels[i],
        text=str(int(val)) if float(val).is_integer() else f"{val}",
        showarrow=False, font=dict(size=12)
    )

fig.update_layout(
    title="Heat Map of Notifications Received",
    xaxis_title="", yaxis_title="",
    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(autorange="reversed"),   # keep top = largest
    height=bar_height,
    margin=dict(l=120, r=40, t=60, b=20)
)

st.plotly_chart(fig, use_container_width=True)
