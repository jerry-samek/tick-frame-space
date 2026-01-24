#!/usr/bin/env python3
"""
analyze_exp56_format.py

Usage:
  python analyze_exp56_format.py --input exp56a_v4_100frags_200k.json[.gz] --outdir results

Requirements:
  pip install pandas numpy matplotlib seaborn tqdm python-dateutil
"""

import os
import sys
import json
import gzip
import argparse
from collections import defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

sns.set(style="whitegrid", context="talk")

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def load_json(path):
    if path.endswith('.gz'):
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    else:
        with open(path, 'r') as f:
            return json.load(f)

def build_summary_df(data):
    snaps = data.get('snapshots', [])
    rows = []
    for s in snaps:
        row = {
            'tick': s.get('tick'),
            'r_mean': s.get('cloud_radius_mean', np.nan),
            'r_rms': s.get('cloud_radius_rms', np.nan),
            'r_std': s.get('cloud_radius_std', np.nan),
            'KE': s.get('total_kinetic_energy', np.nan),
            'PE': s.get('total_potential_energy', np.nan),
            'E_total': s.get('total_energy', np.nan),
            'L': s.get('angular_momentum', np.nan),
            'collisions_total': s.get('total_collisions', np.nan),
            'collisions_tick': s.get('collisions_tick', s.get('collisions_per_tick', np.nan)),
            'fragment_ke_mean': s.get('fragment_ke_mean', np.nan),
            'fragment_ke_std': s.get('fragment_ke_std', np.nan)
        }
        rows.append(row)
    df = pd.DataFrame(rows).sort_values('tick').reset_index(drop=True)
    return df

def plot_time_series(df, outdir):
    ensure_dir(outdir)
    # r_rms (log)
    plt.figure(figsize=(10,4))
    plt.plot(df['tick'], df['r_rms'], label='r_rms', alpha=0.85)
    plt.yscale('log')
    plt.xlabel('tick'); plt.ylabel('r_rms (log)')
    plt.title('r_rms over time (log scale)')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'r_rms_timeseries.png'), dpi=150)
    plt.close()

    # Energies
    plt.figure(figsize=(10,4))
    plt.plot(df['tick'], df['E_total'], label='E_total')
    plt.plot(df['tick'], df['KE'], label='KE')
    plt.plot(df['tick'], df['PE'], label='PE')
    plt.xlabel('tick'); plt.ylabel('energy')
    plt.legend()
    plt.title('Energy components over time')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'energies_timeseries.png'), dpi=150)
    plt.close()

    # collisions per tick
    if not df['collisions_tick'].isna().all():
        plt.figure(figsize=(8,4))
        plt.plot(df['tick'], df['collisions_tick'].fillna(0), label='collisions/tick')
        plt.xlabel('tick'); plt.ylabel('collisions per tick')
        plt.title('Collisions per tick')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'collisions_per_tick.png'), dpi=150)
        plt.close()

    # Angular momentum
    if not df['L'].isna().all():
        plt.figure(figsize=(8,4))
        plt.plot(df['tick'], df['L'], label='L (scalar)')
        plt.xlabel('tick'); plt.ylabel('L')
        plt.title('Angular momentum over time')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, 'L_timeseries.png'), dpi=150)
        plt.close()

def extract_per_fragment(data, outdir, max_ticks_to_dump=500):
    """
    If snapshots contain 'per_fragment' arrays, dump them to CSV per tick
    and build an index. If per_fragment absent, returns empty dict.
    """
    ensure_dir(outdir)
    per_index = {}
    for s in data.get('snapshots', []):
        tick = s.get('tick')
        pf = s.get('per_fragment')
        if not pf:
            continue
        # limit how many ticks we dump to avoid huge disk usage
        if len(per_index) >= max_ticks_to_dump:
            break
        fname = os.path.join(outdir, f'fragments_{tick}.csv')
        df_pf = pd.DataFrame(pf)
        df_pf.to_csv(fname, index=False)
        per_index[tick] = fname
    # save index
    idx_path = os.path.join(outdir, 'per_fragment_index.csv')
    pd.DataFrame([{'tick':t,'file':f} for t,f in per_index.items()]).to_csv(idx_path, index=False)
    return per_index

def build_escape_table_from_files(per_index, outdir):
    rows = []
    for tick, fname in per_index.items():
        df = pd.read_csv(fname)
        # expect column 'total_energy' or similar
        te_col = None
        for c in ['total_energy','totalEnergy','E_total','energy_total']:
            if c in df.columns:
                te_col = c; break
        if te_col is None:
            continue
        # select escaping fragments
        esc = df[df[te_col] >= 0]
        for _, r in esc.iterrows():
            rows.append({
                'tick': tick,
                'id': r.get('id', np.nan),
                'r': r.get('r', np.nan),
                'vx': r.get('vx', np.nan),
                'vy': r.get('vy', np.nan),
                'vz': r.get('vz', np.nan),
                'total_energy': r.get(te_col, np.nan),
                'last_collision_energy': r.get('last_collision_energy', np.nan)
            })
    if not rows:
        return pd.DataFrame()
    df_out = pd.DataFrame(rows).sort_values(['tick','id'])
    out_path = os.path.join(outdir, 'escape_table.csv')
    df_out.to_csv(out_path, index=False)
    return df_out

def radial_heatmap_from_files(per_index, outdir, bins=200, rmax_percentile=99.5):
    ensure_dir(outdir)
    ticks = sorted(per_index.keys())
    radii_list = []
    tick_list = []
    for t in ticks:
        df = pd.read_csv(per_index[t])
        if 'r' not in df.columns:
            continue
        r = df['r'].dropna().values
        if r.size == 0:
            continue
        tick_list.append(t)
        radii_list.append(r)
    if not radii_list:
        return
    all_r = np.concatenate(radii_list)
    rmax = np.percentile(all_r, rmax_percentile)
    edges = np.linspace(0, rmax, bins+1)
    centers = 0.5*(edges[:-1]+edges[1:])
    H = np.zeros((len(tick_list), bins))
    for i, r in enumerate(radii_list):
        counts, _ = np.histogram(r, bins=edges)
        H[i,:] = counts
    Hn = (H.T / (H.sum(axis=1)+1e-12)).T
    plt.figure(figsize=(10,6))
    plt.imshow(Hn.T, origin='lower', aspect='auto',
               extent=[min(tick_list), max(tick_list), centers[0], centers[-1]],
               cmap='magma')
    plt.colorbar(label='normalized density')
    plt.xlabel('tick'); plt.ylabel('radius')
    plt.title('Radial heatmap (tick vs radius)')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'radial_heatmap.png'), dpi=150)
    plt.close()

def collision_outliers_from_snapshots(data, outdir, window=(70000,120000), top_n=50):
    """
    If snapshots include a 'collisions' list per tick with per-collision energies,
    scan and extract top-N by energy in the window.
    """
    rows = []
    for s in data.get('snapshots', []):
        tick = s.get('tick')
        if tick is None: continue
        if tick < window[0] or tick > window[1]: continue
        collisions = s.get('collisions') or s.get('collision_log') or s.get('per_collision')
        if not collisions: continue
        for c in collisions:
            energy = c.get('delta_energy', c.get('energy', np.nan))
            rows.append({'tick': tick, 'energy': energy, 'ids': c.get('ids', c.get('partners'))})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).sort_values('energy', ascending=False).head(top_n)
    df.to_csv(os.path.join(outdir, 'collision_outliers.csv'), index=False)
    return df

def per_fragment_sample_traces(per_index, outdir, sample_n=20):
    ensure_dir(outdir)
    # collect ids
    id_set = set()
    for t,f in per_index.items():
        df = pd.read_csv(f)
        if 'id' in df.columns:
            id_set.update(df['id'].unique().tolist())
    sample_ids = sorted(list(id_set))[:sample_n]
    traces = {fid: {'tick':[], 'r':[], 'total_energy':[]} for fid in sample_ids}
    for t,f in sorted(per_index.items()):
        df = pd.read_csv(f)
        for fid in sample_ids:
            row = df[df['id']==fid]
            if row.empty: continue
            traces[fid]['tick'].append(t)
            traces[fid]['r'].append(row.iloc[0].get('r', np.nan))
            # detect total_energy column
            te = None
            for c in ['total_energy','totalEnergy','E_total','energy_total']:
                if c in row.columns:
                    te = row.iloc[0].get(c)
                    break
            traces[fid]['total_energy'].append(te)
    # plot
    for fid, data in traces.items():
        if not data['tick']:
            continue
        plt.figure(figsize=(8,3))
        plt.plot(data['tick'], data['r'], label='r')
        plt.xlabel('tick'); plt.ylabel('radius'); plt.title(f'Fragment {fid} radius trace')
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f'frag_{fid}_r.png'), dpi=150)
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Analyze Experiment JSON (exp56 format)')
    parser.add_argument('--input', '-i', required=True, help='Path to JSON or JSON.gz file')
    parser.add_argument('--outdir', '-o', default='results', help='Output directory')
    parser.add_argument('--max_per_fragment_ticks', type=int, default=500, help='Max per-fragment ticks to dump')
    args = parser.parse_args()

    ensure_dir(args.outdir)
    print(f'[{datetime.now()}] Loading {args.input} ...')
    data = load_json(args.input)

    # save config and results summary
    cfg = data.get('config', {})
    res = data.get('results', {})
    pd.Series(cfg).to_csv(os.path.join(args.outdir, 'config.csv'))
    pd.Series(res).to_csv(os.path.join(args.outdir, 'results_summary.csv'))

    print(f'[{datetime.now()}] Building summary dataframe from snapshots ...')
    summary_df = build_summary_df(data)
    summary_df.to_csv(os.path.join(args.outdir, 'summary_timeseries.csv'), index=False)

    print(f'[{datetime.now()}] Plotting time series ...')
    plot_time_series(summary_df, args.outdir)

    print(f'[{datetime.now()}] Extracting per-fragment data (if present) ...')
    per_index = extract_per_fragment(data, args.outdir, max_ticks_to_dump=args.max_per_fragment_ticks)
    if per_index:
        print(f'[{datetime.now()}] Dumped per-fragment data for {len(per_index)} ticks.')
        print(f'[{datetime.now()}] Building escape table ...')
        escape_df = build_escape_table_from_files(per_index, args.outdir)
        if not escape_df.empty:
            print(f'[{datetime.now()}] Escape table saved ({len(escape_df)} rows).')
        else:
            print(f'[{datetime.now()}] No escaping fragments found in dumped ticks.')
        print(f'[{datetime.now()}] Building radial heatmap ...')
        radial_heatmap_from_files(per_index, args.outdir, bins=cfg.get('radial_bins',150))
        print(f'[{datetime.now()}] Building sample per-fragment traces ...')
        per_fragment_sample_traces(per_index, args.outdir, sample_n=20)
    else:
        print(f'[{datetime.now()}] No per-fragment blocks found in snapshots.')

    print(f'[{datetime.now()}] Scanning for collision outliers in snapshots ...')
    coll_out = collision_outliers_from_snapshots(data, args.outdir)
    if not coll_out.empty:
        print(f'[{datetime.now()}] Collision outliers saved.')
    else:
        print(f'[{datetime.now()}] No per-collision logs found in snapshots.')

    print(f'[{datetime.now()}] Done. Results in {args.outdir}')

if __name__ == '__main__':
    main()
