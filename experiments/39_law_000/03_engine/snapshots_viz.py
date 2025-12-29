import pandas as pd
import plotly.express as px
import glob

# ------------------------------------------
# 1) Load CSV snapshots (light version)
# ------------------------------------------

files = sorted(glob.glob("output/snapshot_*.csv"))

dfs = []
for f in files:
    df = pd.read_csv(f)

    # LIGHT MODE: subsample edges to reduce load
    df = df[df["edge_index"] % 5 == 0]   # keep every 5th edge

    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# ------------------------------------------
# 2) Animated 3D scatter
# ------------------------------------------

fig = px.scatter_3d(
    data,
    x="x",
    y="y",
    z="z",
    color="node_a",
    animation_frame="tick",
    opacity=0.7,
    title="Animated 3D Scatter (Light Mode)"
)

fig.update_traces(marker=dict(size=2))
fig.update_layout(
    scene=dict(
        xaxis_title="Node ID (X)",
        yaxis_title="Edge Index (Y)",
        zaxis_title="Tick (Z)"
    )
)

fig.show()
