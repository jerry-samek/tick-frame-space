import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load results
df = pd.read_csv("threshold_surface_results.csv")

# Unique sampling factors
for M in sorted(df['M'].unique()):
    subset = df[df['M'] == M]
    pivot = subset.pivot(index='alpha_0', columns='gamma', values='total_agent_commits')
    
    plt.figure(figsize=(8,6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="viridis", cbar_kws={'label': 'Commits'})
    plt.title(f"Agent Commits vs α₀ and γ (M={M})")
    plt.xlabel("γ (damping)")
    plt.ylabel("α₀ (emission strength)")
    plt.tight_layout()
    plt.savefig(f"heatmap_M{M}.png")
    plt.show()