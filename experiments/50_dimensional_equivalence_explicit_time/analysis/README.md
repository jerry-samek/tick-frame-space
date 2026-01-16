# Analysis: Dimensional Equivalence Testing

## Purpose

Compare (n+t) results against (n+1) baseline to determine if time behaves as a dimension.

## Comparison Matrix

| Variant | Configuration | Baseline | Hypothesis |
|---------|--------------|----------|------------|
| A | 2D+t | 3D | Equiv if match |
| A | 3D+t | 4D | Equiv if match |
| A | 4D+t | 5D | Equiv if match |
| B | 2D+t | 3D | Differ if time=param |
| B | 3D+t | 4D | Differ if time=param |
| B | 4D+t | 5D | Differ if time=param |

## Analysis Scripts

**compare_metrics.py**: Statistical comparison of CV, ρ, gradient
**plot_overlays.py**: Overlay plots of (n+t) vs (n+1)
**anomaly_classification.py**: Compare anomaly patterns
**scaling_laws.py**: Test dimensional scaling predictions
**theory_doc_50_checklist.py**: Generate Theory Doc 50 checklist

## Metrics

**Primary**:
- Mean absolute error: |metric(n+t) - metric(n+1)|
- Relative error: |metric(n+t) - metric(n+1)| / metric(n+1)
- Correlation coefficient: corr(n+t, n+1)

**Threshold**: 10% relative error = **equivalence boundary**

## Deliverables

- CSV: summary_comparison.csv
- Plots: comparison_*.png (one per metric)
- Report: RESULTS.md with conclusion
