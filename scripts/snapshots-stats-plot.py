import csv, math
import matplotlib.pyplot as plt

# Edit with your CSV paths and frame labels
frames = [
    ("frame_13000_stats.csv", "13000"),
    ("frame_2200_stats.csv", "2200"),
    ("frame_3300_stats.csv", "3300"),
]

def parse_stats(path):
    out = {}
    with open(path, newline="") as f:
        r = csv.reader(f)
        for k, v in r:
            out[k] = v
    def parse_bbox(s):
        s = s.strip().strip('"').strip("'")
        # Expecting {'min': -447, 'max': 702}
        parts = s.replace("{", "").replace("}", "").split(",")
        vals = {}
        for p in parts:
            k2, v2 = p.split(":")
            k2 = k2.strip().strip('"').strip("'")
            vals[k2] = float(v2)
        return vals["min"], vals["max"]
    min_x, max_x = parse_bbox(out["Bounding Box X"])
    min_y, max_y = parse_bbox(out["Bounding Box Y"])
    min_z, max_z = parse_bbox(out["Bounding Box Z"])
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    cz = (min_z + max_z) / 2.0
    com_mag = math.sqrt(cx*cx + cy*cy + cz*cz)
    ex = max_x - min_x
    ey = max_y - min_y
    ez = max_z - min_z
    avg_radius = float(out["Average Radius"])
    entities = int(float(out["Total Entities"]))
    return {
        "frame": path,
        "label": out.get("Metric", "") or path,
        "entities": entities,
        "avg_radius": avg_radius,
        "cx": cx, "cy": cy, "cz": cz, "com_mag": com_mag,
        "ex": ex, "ey": ey, "ez": ez,
    }

rows = [parse_stats(p) | {"label": lbl} for p, lbl in frames]

# Plot COM magnitude
plt.figure(figsize=(7,4))
plt.plot([r["label"] for r in rows], [r["com_mag"] for r in rows], marker="o", color="teal")
plt.title("Estimated center-of-mass magnitude from bounding boxes")
plt.xlabel("Frame")
plt.ylabel("COM magnitude (approx.)")
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()

# Plot axis extents
plt.figure(figsize=(7,4))
labels = [r["label"] for r in rows]
plt.plot(labels, [r["ex"] for r in rows], marker="o", label="X extent", color="crimson")
plt.plot(labels, [r["ey"] for r in rows], marker="o", label="Y extent", color="orange")
plt.plot(labels, [r["ez"] for r in rows], marker="o", label="Z extent", color="olive")
plt.title("Bounding box asymmetry over frames")
plt.xlabel("Frame")
plt.ylabel("Extent (max - min)")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
