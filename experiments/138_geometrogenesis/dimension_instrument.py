"""Exp 138 P1d — null-safe dimension instrument (PREREG_I0prime.md).

is_manifold gate = (shell classifier reads poly) AND (4-cycle density high).
Random regular graphs fool spectral d_s (P1c) but fail BOTH of these:
they read shell-exp and are locally tree-like (~0 short cycles). d_spectral
is reported as the dimension value, not gated.
"""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from instrument import fit_exponent, shell_counts   # noqa: E402
from p1c_recon import ds_sparse                      # noqa: E402

CYC_THRESH = 0.35  # frozen by G-I0'; overwritten from results/i0prime.json when present

def short_cycle_density(adj):
    """Mean number of undirected 4-cycles through a node."""
    sets = [set(adj[i]) for i in range(len(adj))]
    total = 0
    for v in range(len(adj)):
        nb = sorted(sets[v])
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                # common neighbours of nb[i],nb[j] other than v => 4-cycle v-nb[i]-x-nb[j]
                total += len((sets[nb[i]] & sets[nb[j]]) - {v})
    return total / (2 * len(adj))  # each 4-cycle counted twice per node pair

def classify_dimension(adj, rng, n_sources=64):
    nbar = shell_counts(adj, sorted(int(x) for x in
                        (rng.choice(len(adj), min(n_sources, len(adj)), replace=False)
                         if len(adj) > n_sources else range(len(adj)))))
    shell = fit_exponent(nbar)
    cyc = short_cycle_density(adj)
    d_spec = ds_sparse(adj) if len(adj) >= 64 else float("nan")
    is_manifold = (shell["cls"] == "poly") and (cyc >= CYC_THRESH)
    return {"shell_cls": shell["cls"], "d_shell": shell["e_hat"],
            "d_spectral": d_spec, "cyc_density": cyc,
            "is_manifold": bool(is_manifold)}
