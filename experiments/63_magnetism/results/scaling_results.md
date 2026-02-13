# Scaling Experiment Results

**Date**: 2026-02-12
**Mode**: signed only
**Parameters**: eq=1000, probe=2000, runs=3, speed=0.5

## Configurations

| Config | Grid | Entities | Spacing | Purpose |
|--------|------|----------|---------|---------|
| 64x64_4x4 | 64x64 | 4x4 (16) | 16 | Baseline |
| 128x128_4x4 | 128x128 | 4x4 (16) | 32 | 2x resolution |
| 256x256_4x4 | 256x256 | 4x4 (16) | 64 | 4x resolution |
| 64x64_8x8 | 64x64 | 8x8 (64) | 8 | 4x entity density |

## Transport Anisotropy — Signal vs Noise

| Config | Pattern | |A_NS| | std | |A_EW| | std | |defl| | std | SNR |
|--------|---------|--------|-----|--------|-----|-------|-----|-----|
| 64x64_4x4 | checkerboard | 0.3584 | 0.5274 | 1.0993 | 1.3136 | 1.1914 | 1.3711 | 0.87 |
| 64x64_4x4 | stripe | 0.2593 | 0.4529 | 0.0245 | 0.8414 | 0.7351 | 0.4520 | 1.63 |
| 128x128_4x4 | checkerboard | 0.0890 | 2.0941 | 0.4399 | 1.4478 | 2.0763 | 0.5631 | 3.69 |
| 128x128_4x4 | stripe | 0.9628 | 0.1816 | 0.0859 | 1.1559 | 1.3476 | 0.2161 | 6.24 |
| 256x256_4x4 | checkerboard | 1.0523 | 0.8867 | 0.0008 | 1.2270 | 1.5107 | 0.7278 | 2.08 |
| 256x256_4x4 | stripe | 0.8226 | 1.1981 | 0.8575 | 0.4638 | 1.4578 | 0.7622 | 1.91 |
| 64x64_8x8 | checkerboard | 0.8438 | 0.4434 | 0.3972 | 1.0799 | 1.2543 | 0.5546 | 2.26 |
| 64x64_8x8 | stripe | 0.0469 | 1.2801 | 1.4090 | 1.4040 | 1.7849 | 1.3462 | 1.33 |

SNR = |mean deflection| / std(deflection). Higher = cleaner signal.
If SNR increases with resolution, the physics is real.
If SNR stays flat or decreases, it's lattice noise.

## M_net (Compensated Magnetism)

| Config | Checkerboard | Stripe | Ferromagnetic | Antiferromagnetic |
|--------|-------------|--------|---------------|-------------------|
| 64x64_4x4 | 2.19e-13 | 1.82e-12 | 80000.0 | 4.55e-13 |
| 128x128_4x4 | 3.50e-13 | 2.61e-12 | 80000.0 | 1.52e-12 |
| 256x256_4x4 | 1.10e-12 | 6.55e-13 | 80000.0 | 3.64e-12 |
| 64x64_8x8 | 3.83e-13 | 1.34e-12 | 320000.0 | 2.65e-13 |

## Fourier Angular Modes

| Config | Pattern | m=1 | m=2 | m=4 | m=6 | m=8 | Dominant |
|--------|---------|-----|-----|-----|-----|-----|----------|
| 64x64_4x4 | checkerboard | 0.066 | 0.070 | 0.222 | 0.058 | 0.482 | m=8 |
| 64x64_4x4 | stripe | 0.002 | 0.025 | 0.512 | 0.016 | 0.445 | m=4 |
| 64x64_4x4 | antiferromagnetic | 0.026 | 0.024 | 0.071 | 0.085 | 0.767 | m=8 |
| 128x128_4x4 | checkerboard | 0.056 | 0.074 | 0.328 | 0.076 | 0.380 | m=8 |
| 128x128_4x4 | stripe | 0.001 | 0.012 | 0.507 | 0.007 | 0.472 | m=4 |
| 128x128_4x4 | antiferromagnetic | 0.016 | 0.025 | 0.064 | 0.120 | 0.755 | m=8 |
| 256x256_4x4 | checkerboard | 0.053 | 0.121 | 0.178 | 0.138 | 0.426 | m=8 |
| 256x256_4x4 | stripe | 0.011 | 0.054 | 0.311 | 0.023 | 0.589 | m=8 |
| 256x256_4x4 | antiferromagnetic | 0.024 | 0.157 | 0.121 | 0.328 | 0.335 | m=8 |
| 64x64_8x8 | checkerboard | 0.071 | 0.147 | 0.038 | 0.076 | 0.493 | m=8 |
| 64x64_8x8 | stripe | 0.007 | 0.013 | 0.487 | 0.011 | 0.478 | m=4 |
| 64x64_8x8 | antiferromagnetic | 0.024 | 0.009 | 0.346 | 0.049 | 0.547 | m=8 |

## Off-Diagonal Conductivity (sigma_xy)

| Config | Checkerboard | Stripe | Ferromagnetic | Antiferromagnetic |
|--------|-------------|--------|---------------|-------------------|
| 64x64_4x4 | 0.0439 | -0.0383 | 0.0146 | -0.0352 |
| 128x128_4x4 | 0.0295 | -0.1045 | 0.1702 | 0.0265 |
| 256x256_4x4 | 0.2052 | -0.0675 | 0.0111 | 0.0307 |
| 64x64_8x8 | -0.2089 | 0.0095 | -0.1430 | 0.0438 |