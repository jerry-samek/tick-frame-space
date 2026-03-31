#!/usr/bin/env python3
"""
Experiment 118 v7: N-gram Stream Filtering — Structure vs Frequency

Feed raw byte streams through consumption-transformation-rejection hierarchy.
Compare N=1 (bytes), N=2 (bigrams), N=4 (4-grams), N=8 (8-grams)
across English text, DNA, and random data.

If depth increases with N for structured data but not random →
mechanism discovers sequential structure.
"""

import os
import sys
import math
import time
import csv
import random as stdlib_random
from collections import Counter, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Config ------------------------------------------------------------------
LEARNING_WINDOW = 2000      # ticks to observe before crystallizing spectrum
TARGET_COVERAGE = 0.5       # fraction of stream to learn to consume
SEED_THRESHOLD  = 60        # tokens before seed → child entity
TICKS           = 100_000
MAX_DEPTH       = 20        # safety cap on hierarchy depth
NGRAM_SIZES     = [1, 2, 4, 8]
DATA_SIZE       = 500_000   # bytes per data source
LOG_EVERY       = 10_000

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "results")
DATA = os.path.join(BASE, "data")


# --- Data Generation ---------------------------------------------------------

def generate_english(path, size):
    """Generate English-like text from common words with Zipf weighting."""
    rng = stdlib_random.Random(42)
    words = (
        "the of and to a in is it that was for on are with as his they be "
        "at one have this from by not but some what there we can out other "
        "were all your when up use how said each she which do their time "
        "if will way about many then them would write like so these her "
        "long make thing see him two has look more day could go come did "
        "my sound no most number who over know water than call first "
        "people may down side been now find head stand own page should "
        "country found answer school grow study still learn plant never "
        "great world through"
    ).split()
    weights = [100.0 / (i + 1) ** 0.8 for i in range(len(words))]
    with open(path, 'wb') as f:
        written = 0
        while written < size:
            word = rng.choices(words, weights=weights)[0]
            sep = b'\n' if rng.random() < 0.05 else b' '
            chunk = sep + word.encode() if written > 0 else word.encode()
            f.write(chunk)
            written += len(chunk)


def generate_dna(path, size):
    """Generate DNA with codon-frequency bias (3-byte periodicity)."""
    rng = stdlib_random.Random(42)
    codons = [
        ('ATG', 5), ('TTT', 8), ('TTC', 6), ('TTA', 3), ('TTG', 5),
        ('CTT', 5), ('CTC', 4), ('CTA', 2), ('CTG', 8), ('ATT', 6),
        ('ATC', 5), ('ATA', 3), ('GTT', 4), ('GTC', 3), ('GTA', 2),
        ('GTG', 6), ('TCT', 5), ('TCC', 4), ('TCA', 3), ('TCG', 1),
        ('CCT', 4), ('CCC', 3), ('CCA', 4), ('CCG', 2), ('ACT', 3),
        ('ACC', 4), ('ACA', 3), ('ACG', 2), ('GCT', 5), ('GCC', 4),
        ('GCA', 3), ('GCG', 2), ('TAT', 3), ('TAC', 3), ('CAT', 3),
        ('CAC', 3), ('CAA', 3), ('CAG', 5), ('AAT', 4), ('AAC', 4),
        ('AAA', 6), ('AAG', 5), ('GAT', 4), ('GAC', 3), ('GAA', 5),
        ('GAG', 4), ('TGT', 2), ('TGC', 2), ('TGG', 2), ('CGT', 1),
        ('CGC', 2), ('CGA', 1), ('CGG', 2), ('AGT', 2), ('AGC', 3),
        ('AGA', 3), ('AGG', 2), ('GGT', 2), ('GGC', 3), ('GGA', 3),
        ('GGG', 2), ('TAA', 1), ('TAG', 1), ('TGA', 2),
    ]
    names, weights = zip(*codons)
    with open(path, 'wb') as f:
        written = 0
        while written < size:
            codon = rng.choices(names, weights=weights)[0]
            f.write(codon.encode())
            written += 3


def generate_random(path, size):
    """Generate uniform random bytes."""
    with open(path, 'wb') as f:
        f.write(os.urandom(size))


# --- N-gram Stream -----------------------------------------------------------

def ngram_stream(data, n):
    """Yield sliding-window n-gram tuples from data bytes, wrapping at end."""
    length = len(data)
    i = 0
    while True:
        yield tuple(data[(i + j) % length] for j in range(n))
        i += 1


# --- Statistics --------------------------------------------------------------

def shannon_entropy(data):
    """Shannon entropy in bits per byte."""
    counts = Counter(data)
    total = len(data)
    return -sum(c / total * math.log2(c / total) for c in counts.values())


def sequential_mutual_info(data):
    """I(X_i ; X_{i-1}) = H(X) - H(X | X_{i-1})."""
    counts_x = Counter(data)
    total = len(data)
    h_x = -sum(c / total * math.log2(c / total) for c in counts_x.values())

    bigrams = Counter()
    prev_counts = Counter()
    for i in range(1, len(data)):
        bigrams[(data[i - 1], data[i])] += 1
        prev_counts[data[i - 1]] += 1

    denom = total - 1
    h_cond = 0.0
    for (p, _), cnt in bigrams.items():
        p_joint = cnt / denom
        p_cond = cnt / prev_counts[p]
        h_cond -= p_joint * math.log2(p_cond)

    return h_x - h_cond


def fmt_ngram(t):
    """Human-readable n-gram display."""
    try:
        s = bytes(t).decode('ascii')
        if all(c.isprintable() or c in ' \n\t' for c in s):
            return repr(s)
    except Exception:
        pass
    return '(' + ','.join(f'{b:02x}' for b in t) + ')'


# --- Entity Model ------------------------------------------------------------

class Seed:
    """Accumulates rejected tokens until promoted to a child entity."""
    __slots__ = ('tokens', 'birth_tick')

    def __init__(self, tick):
        self.tokens = []
        self.birth_tick = tick

    def feed(self, token):
        self.tokens.append(token)


class Entity:
    """Stream-filtering entity that learns a spectrum and consumes/rejects."""

    def __init__(self, name, depth=0, parent=None, birth_tick=0):
        self.name = name
        self.depth = depth
        self.parent = parent
        self.birth_tick = birth_tick
        self.spectrum = set()       # known n-grams (after crystallization)
        self.learning = True
        self.obs_counts = Counter() # frequency counts during learning
        self.learning_ticks = 0
        self.consumed = 0           # tokens consumed (mass)
        self.rejected = 0           # tokens rejected
        self.children = []
        self.seed = None            # at most one active seed

    def observe(self, token):
        """During learning phase, count frequencies."""
        self.obs_counts[token] += 1
        self.learning_ticks += 1
        if self.learning_ticks >= LEARNING_WINDOW:
            self._crystallize()

    def _crystallize(self):
        """Learn spectrum from observations: most common covering TARGET_COVERAGE."""
        total = sum(self.obs_counts.values())
        if total == 0:
            self.learning = False
            return
        cum = 0
        for ngram, count in self.obs_counts.most_common():
            self.spectrum.add(ngram)
            cum += count
            if cum / total >= TARGET_COVERAGE:
                break
        self.learning = False
        self.obs_counts.clear()

    def grow(self):
        self.consumed += 1

    def mass(self):
        return self.consumed


# --- Token Processing --------------------------------------------------------

def process(entity, token, tick, all_entities, events):
    """Route one token through the entity tree (cascade model).

    Each entity consumes tokens matching its spectrum and forwards ALL
    rejects to its child.  The child runs the same logic — consume or
    reject — so depth emerges from cascading rejection streams.
    """
    # Learning phase: observe only
    if entity.learning:
        entity.observe(token)
        return

    # Known pattern → consume
    if token in entity.spectrum:
        entity.grow()
        return

    # Unknown → reject → cascade to child
    entity.rejected += 1

    # Forward ALL rejects to existing child (cascade — no spectrum pre-check)
    if entity.children:
        process(entity.children[0], token, tick, all_entities, events)
        return

    # No child yet → accumulate in seed
    if entity.depth >= MAX_DEPTH:
        return

    if entity.seed is None:
        entity.seed = Seed(tick)
    entity.seed.feed(token)

    # Promote seed → child entity?
    if len(entity.seed.tokens) >= SEED_THRESHOLD:
        name = f"d{entity.depth + 1}_e{len(all_entities)}"
        child = Entity(name, depth=entity.depth + 1,
                       parent=entity, birth_tick=tick)
        # Pre-load observations from accumulated seed tokens
        for t in entity.seed.tokens:
            child.obs_counts[t] += 1
            child.learning_ticks += 1
        if child.learning_ticks >= LEARNING_WINDOW:
            child._crystallize()
        entity.children.append(child)
        all_entities.append(child)
        events.append((tick, name, child.depth))
        entity.seed = None


# --- Tree Display ------------------------------------------------------------

def print_tree(entity, total, prefix="", is_last=True, max_depth=10):
    """Print entity hierarchy."""
    if entity.depth > max_depth:
        return
    pct = 100 * entity.consumed / total if total > 0 else 0
    spec = len(entity.spectrum)
    status = "learning" if entity.learning else f"spec={spec}"
    born = f" born={entity.birth_tick}" if entity.depth > 0 else ""
    connector = "`-- " if entity.depth > 0 else ""
    print(f"{prefix}{connector}{entity.name}  "
          f"consumed={entity.consumed} ({pct:.1f}%)  "
          f"{status}{born}")

    child_prefix = prefix + ("    " if is_last else "|   ")
    items = list(entity.children)
    if entity.seed:
        items = items + [entity.seed]

    for i, item in enumerate(items):
        last = (i == len(items) - 1)
        if isinstance(item, Entity):
            print_tree(item, total, child_prefix, last, max_depth)
        else:
            conn = "`-- " if last else "|-- "
            print(f"{child_prefix}{conn}[seed: "
                  f"{len(item.tokens)}/{SEED_THRESHOLD}]")

    # Summary for truncated subtrees
    if entity.depth == max_depth:
        deep = sum(1 for c in entity.children if c.depth > max_depth)
        if deep:
            print(f"{child_prefix}  ... {deep} deeper entities omitted")


# --- Single Run --------------------------------------------------------------

def run_single(source_name, data, ngram_n, ticks):
    """Run one (source, N) configuration. Returns result dict."""
    # Use full data for statistics — small samples cause severe MI bias
    # (plugin estimator bias ≈ (|X|-1)^2 / 2N·ln2 ≈ 0.94 bits for 50K bytes)
    entropy = shannon_entropy(data)
    mut_info = sequential_mutual_info(data)

    print(f"\n{'=' * 60}")
    print(f"{source_name} N={ngram_n}")
    print(f"  entropy={entropy:.2f} bits/byte  mut_info={mut_info:.3f} bits")

    root = Entity("root", depth=0, birth_tick=0)
    all_entities = [root]
    events = []
    stream = ngram_stream(data, ngram_n)
    rec = defaultdict(list)

    t0 = time.time()
    for tick in range(ticks):
        token = next(stream)
        process(root, token, tick, all_entities, events)

        if (tick + 1) % LOG_EVERY == 0:
            max_d = max(e.depth for e in all_entities)
            n_ent = len(all_entities)
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick + 1:>6}  entities={n_ent:>3}  depth={max_d}  "
                  f"root_consumed={root.consumed:>6}  ({rate:.0f} t/s)")
            rec['t'].append(tick + 1)
            rec['n_entities'].append(n_ent)
            rec['max_depth'].append(max_d)
            rec['root_consumed'].append(root.consumed)

    elapsed = time.time() - t0
    max_depth = max(e.depth for e in all_entities)
    total_consumed = sum(e.consumed for e in all_entities)
    root_pct = 100 * root.consumed / total_consumed if total_consumed else 0

    mass_by_depth = defaultdict(int)
    count_by_depth = defaultdict(int)
    for e in all_entities:
        mass_by_depth[e.depth] += e.consumed
        count_by_depth[e.depth] += 1

    # Consumed depth: deepest entity with consumed > 0
    consumed_depth = max((e.depth for e in all_entities if e.consumed > 0),
                         default=0)

    print(f"\n  --- Result ---")
    print(f"  Depth: {max_depth}  Consumed depth: {consumed_depth}  "
          f"Entities: {len(all_entities)}")
    print(f"  Root consumed: {root.consumed} ({root_pct:.1f}%)")
    print(f"  Root spectrum: {len(root.spectrum)} n-grams")
    print(f"  Time: {elapsed:.1f}s")

    # Show root spectrum sample for interpretable cases
    if root.spectrum and ngram_n <= 4:
        sample_grams = sorted(root.spectrum)[:10]
        print(f"  Root spectrum sample: "
              + ", ".join(fmt_ngram(t) for t in sample_grams))

    print()
    print_tree(root, total_consumed)

    return {
        'source': source_name,
        'n': ngram_n,
        'entropy': entropy,
        'mut_info': mut_info,
        'depth': max_depth,
        'consumed_depth': consumed_depth,
        'n_entities': len(all_entities),
        'root_pct': root_pct,
        'root_spectrum_size': len(root.spectrum),
        'mass_by_depth': dict(mass_by_depth),
        'count_by_depth': dict(count_by_depth),
        'all_entities': all_entities,
        'events': events,
        'timeseries': dict(rec),
        'elapsed': elapsed,
    }


# --- Plotting ----------------------------------------------------------------

def plot_results(results):
    """Generate comparison plots across all runs."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "Exp 118 v7: N-gram Stream Filtering \u2014 Structure vs Frequency\n"
        f"LEARNING={LEARNING_WINDOW}  COVERAGE={TARGET_COVERAGE}  "
        f"SEED={SEED_THRESHOLD}  TICKS={TICKS}",
        fontsize=11)

    sources = ['english', 'dna', 'random']
    colors = {'english': 'tab:blue', 'dna': 'tab:green', 'random': 'tab:red'}
    markers = {'english': 'o', 'dna': 's', 'random': '^'}
    ns = sorted(set(r['n'] for r in results))

    # --- Row 0, Col 0: Consumed Depth vs N (key metric) ---
    ax = axes[0, 0]
    for src in sources:
        d = sorted([r for r in results if r['source'] == src],
                   key=lambda r: r['n'])
        ax.plot([r['n'] for r in d], [r['consumed_depth'] for r in d],
                f'-{markers[src]}', color=colors[src], label=src, lw=2)
    ax.set(xlabel='N-gram size', ylabel='Consumed Depth',
           title='Consumed Depth vs N\n(deepest entity with consumption > 0)')
    ax.set_xticks(ns)
    ax.legend()

    # --- Row 0, Col 1: Raw Depth vs N ---
    ax = axes[0, 1]
    for src in sources:
        d = sorted([r for r in results if r['source'] == src],
                   key=lambda r: r['n'])
        ax.plot([r['n'] for r in d], [r['depth'] for r in d],
                f'-{markers[src]}', color=colors[src], label=src, lw=2,
                alpha=0.7)
    ax.axhline(y=MAX_DEPTH, color='gray', ls='--', lw=0.8, label='MAX_DEPTH')
    ax.set(xlabel='N-gram size', ylabel='Raw Depth',
           title='Raw Depth vs N\n(includes empty entities)')
    ax.set_xticks(ns)
    ax.legend(fontsize=8)

    # --- Row 0, Col 2: Root consumption % vs N ---
    ax = axes[0, 2]
    for src in sources:
        d = sorted([r for r in results if r['source'] == src],
                   key=lambda r: r['n'])
        ax.plot([r['n'] for r in d], [r['root_pct'] for r in d],
                f'-{markers[src]}', color=colors[src], label=src, lw=2)
    ax.set(xlabel='N-gram size', ylabel='Root %',
           title='Root Consumption vs N')
    ax.set_xticks(ns)
    ax.legend()

    # --- Row 1: Mass distribution by depth, one panel per source ---
    for i, src in enumerate(sources):
        ax = axes[1, i]
        src_results = sorted(
            [r for r in results if r['source'] == src],
            key=lambda r: r['n'])
        max_d = max((r['depth'] for r in src_results), default=0)
        if max_d == 0:
            ax.set_title(f'{src}: no hierarchy')
            continue
        depths = list(range(max_d + 1))
        n_runs = len(src_results)
        width = 0.8 / max(n_runs, 1)
        for j, r in enumerate(src_results):
            total_mass = sum(r['mass_by_depth'].values())
            if total_mass == 0:
                continue
            fracs = [r['mass_by_depth'].get(d, 0) / total_mass
                     for d in depths]
            offsets = [d + (j - n_runs / 2 + 0.5) * width for d in depths]
            ax.bar(offsets, fracs, width=width,
                   label=f'N={r["n"]}', alpha=0.8)
        ax.set(xlabel='Depth', ylabel='Mass fraction',
               title=f'{src}: Mass by Depth')
        ax.set_xticks(depths)
        ax.legend(fontsize=8)

    plt.tight_layout()
    fig_path = os.path.join(OUT, 'v7_results.png')
    plt.savefig(fig_path, dpi=150)
    print(f"\nPlot: {fig_path}")


# --- Main --------------------------------------------------------------------

def run():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)

    paths = {
        'english': os.path.join(DATA, 'english.txt'),
        'dna':     os.path.join(DATA, 'dna.txt'),
        'random':  os.path.join(DATA, 'random.bin'),
    }

    # Generate data sources if missing
    if not os.path.exists(paths['english']):
        print("Generating English text...")
        generate_english(paths['english'], DATA_SIZE)
    if not os.path.exists(paths['dna']):
        print("Generating DNA sequence...")
        generate_dna(paths['dna'], DATA_SIZE)
    if not os.path.exists(paths['random']):
        print("Generating random bytes...")
        generate_random(paths['random'], DATA_SIZE)

    # Load all data into memory
    source_data = {}
    for name, path in paths.items():
        with open(path, 'rb') as f:
            source_data[name] = f.read()
        print(f"  {name}: {len(source_data[name])} bytes")

    # Run all (source, N) configurations
    results = []
    for source in ['english', 'dna', 'random']:
        for n in NGRAM_SIZES:
            r = run_single(source, source_data[source], n, TICKS)
            results.append(r)

    # --- Summary Table ---
    print(f"\n{'=' * 90}")
    print("SUMMARY TABLE")
    print(f"{'=' * 90}")
    print(f"{'Source':<10} {'N':>2} {'Entropy':>8} {'MutInfo':>8} "
          f"{'Depth':>6} {'ConsDep':>8} {'Entities':>9} {'Root%':>6} "
          f"{'Spectrum':>9}")
    print('-' * 90)
    for r in results:
        print(f"{r['source']:<10} {r['n']:>2} {r['entropy']:>8.2f} "
              f"{r['mut_info']:>8.3f} {r['depth']:>6} "
              f"{r['consumed_depth']:>8} "
              f"{r['n_entities']:>9} {r['root_pct']:>5.1f}% "
              f"{r['root_spectrum_size']:>9}")

    # --- Summary CSV ---
    csv_path = os.path.join(OUT, 'v7_summary.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source', 'n', 'entropy', 'mut_info', 'depth',
                     'consumed_depth', 'n_entities', 'root_pct',
                     'root_spectrum_size'])
        for r in results:
            w.writerow([r['source'], r['n'], f"{r['entropy']:.4f}",
                        f"{r['mut_info']:.4f}", r['depth'],
                        r['consumed_depth'],
                        r['n_entities'], f"{r['root_pct']:.2f}",
                        r['root_spectrum_size']])
    print(f"\nCSV: {csv_path}")

    # --- Per-entity CSV ---
    ent_csv = os.path.join(OUT, 'v7_entities.csv')
    with open(ent_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source', 'n', 'name', 'depth', 'parent',
                     'spectrum_size', 'consumed', 'rejected', 'birth_tick'])
        for r in results:
            for e in r['all_entities']:
                w.writerow([r['source'], r['n'], e.name, e.depth,
                            e.parent.name if e.parent else '',
                            len(e.spectrum), e.consumed, e.rejected,
                            e.birth_tick])
    print(f"Entity CSV: {ent_csv}")

    plot_results(results)


if __name__ == '__main__':
    run()
