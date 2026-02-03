import numpy as np
import csv

# ============================================================
# Experiment 77 v1 — Run 1D, 2D, 3D and export CSV results
# ============================================================

N = 101
TICKS = 200
GAMMA_0 = 0.0
A = 1.0
NORMALIZE_MASS = True


# ------------------------------------------------------------
# Field creation
# ------------------------------------------------------------
def create_field(dim, N, gamma0, A):
    if dim == 1:
        f = np.full((N,), gamma0)
        f[N//2] += A
    elif dim == 2:
        f = np.full((N, N), gamma0)
        f[N//2, N//2] += A
    elif dim == 3:
        f = np.full((N, N, N), gamma0)
        f[N//2, N//2, N//2] += A
    return f


# ------------------------------------------------------------
# Kernels
# ------------------------------------------------------------
def kernel_1d():
    return np.array([0.25, 0.5, 0.25])

def kernel_2d():
    K = np.array([[1, 2, 1],
                  [2, 4, 2],
                  [1, 2, 1]], dtype=float)
    return K / K.sum()

def kernel_3d():
    k1 = np.array([1, 2, 1], dtype=float)
    k1 = k1 / k1.sum()
    K2 = np.outer(k1, k1)
    K3 = np.zeros((3, 3, 3))
    for z in range(3):
        K3[z] = K2 * k1[z]
    return K3 / K3.sum()


# ------------------------------------------------------------
# Smoothing
# ------------------------------------------------------------
def smooth_1d(f, K):
    N = f.shape[0]
    out = np.zeros_like(f)
    for x in range(N):
        acc = 0
        wsum = 0
        for i, w in enumerate(K):
            dx = i - 1
            xx = x + dx
            if 0 <= xx < N:
                acc += w * f[xx]
                wsum += w
        out[x] = acc / wsum
    return out


def smooth_2d(f, K):
    N, M = f.shape
    out = np.zeros_like(f)
    for x in range(N):
        for y in range(M):
            acc = 0
            wsum = 0
            for i in range(3):
                for j in range(3):
                    xx = x + (i - 1)
                    yy = y + (j - 1)
                    if 0 <= xx < N and 0 <= yy < M:
                        w = K[i, j]
                        acc += w * f[xx, yy]
                        wsum += w
            out[x, y] = acc / wsum
    return out


def smooth_3d(f, K):
    N, M, L = f.shape
    out = np.zeros_like(f)
    for x in range(N):
        for y in range(M):
            for z in range(L):
                acc = 0
                wsum = 0
                for i in range(3):
                    for j in range(3):
                        for k in range(3):
                            xx = x + (i - 1)
                            yy = y + (j - 1)
                            zz = z + (k - 1)
                            if 0 <= xx < N and 0 <= yy < M and 0 <= zz < L:
                                w = K[i, j, k]
                                acc += w * f[xx, yy, zz]
                                wsum += w
                out[x, y, z] = acc / wsum
    return out


# ------------------------------------------------------------
# Radial profiles
# ------------------------------------------------------------
def radial_2d(f):
    N, M = f.shape
    cx, cy = N//2, M//2
    rmax = int(np.sqrt(cx**2 + cy**2))
    sums = np.zeros(rmax+1)
    counts = np.zeros(rmax+1)

    for x in range(N):
        for y in range(M):
            r = int(round(np.sqrt((x-cx)**2 + (y-cy)**2)))
            if r <= rmax:
                sums[r] += f[x, y]
                counts[r] += 1

    return sums / np.maximum(counts, 1)


def radial_3d(f):
    N, M, L = f.shape
    cx, cy, cz = N//2, M//2, L//2
    rmax = int(np.sqrt(cx**2 + cy**2 + cz**2))
    sums = np.zeros(rmax+1)
    counts = np.zeros(rmax+1)

    for x in range(N):
        for y in range(M):
            for z in range(L):
                r = int(round(np.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)))
                if r <= rmax:
                    sums[r] += f[x, y, z]
                    counts[r] += 1

    return sums / np.maximum(counts, 1)


# ------------------------------------------------------------
# Run experiment for a dimension
# ------------------------------------------------------------
def run_dim(dim, csv_name, radial_csv=None):
    print(f"Running {dim}D...")

    if dim == 1:
        K = kernel_1d()
    elif dim == 2:
        K = kernel_2d()
    else:
        K = kernel_3d()

    f = create_field(dim, N, GAMMA_0, A)
    initial_mass = f.sum()

    # CSV writers
    with open(csv_name, "w", newline="") as fcsv:
        writer = csv.writer(fcsv)
        writer.writerow(["tick", "peak", "mass"])

        if radial_csv:
            frad = open(radial_csv, "w", newline="")
            wrad = csv.writer(frad)
            wrad.writerow(["tick", "radius", "value"])

        for t in range(TICKS+1):
            peak = f.max()
            mass = f.sum()
            writer.writerow([t, peak, mass])

            if radial_csv:
                if dim == 2:
                    prof = radial_2d(f)
                else:
                    prof = radial_3d(f)
                for r, v in enumerate(prof):
                    wrad.writerow([t, r, v])

            if t == TICKS:
                break

            # evolve
            if dim == 1:
                f = smooth_1d(f, K)
            elif dim == 2:
                f = smooth_2d(f, K)
            else:
                f = smooth_3d(f, K)

            if NORMALIZE_MASS:
                f *= initial_mass / f.sum()

        if radial_csv:
            frad.close()

    print(f"Finished {dim}D → {csv_name}")


# ------------------------------------------------------------
# Run all dimensions
# ------------------------------------------------------------
run_dim(1, "results_1d.csv")
run_dim(2, "results_2d.csv", "radial_2d.csv")
run_dim(3, "results_3d.csv", "radial_3d.csv")

print("All dimensions complete.")
