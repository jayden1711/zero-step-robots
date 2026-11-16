# Warm-start robustness report (addendum docs/addendum-2026-11-16-warmstart-robustness.md)

No LLM was called. Optimiser: CEM (population 20, 5 elites, 25 generations = 500 designs = 5,000 practice episodes), the same starts and budget as the hill climber in results/warmstart_report.md.

## Q1: CEM replication, hopper

Calibration (H): 7 of 10 runs pass by 500.

| set | n | pass by 20 | pass by 100 | pass by 200 | pass by 500 | median d @500 |
|---|---|---|---|---|---|---|
| L | 80 | 1 | 16 | 31 | 34 | 1.95 |
| P | 80 | 0 | 5 | 7 | 8 | 0.94 |
| R | 80 | 0 | 0 | 2 | 2 | 0.59 |
| H | 10 | 0 | 2 | 6 | 7 | 3.39 |

- L vs R (primary), pass by checkpoint 500: 34/80 vs 2/80, difference +0.40, one-sided p = 0.0000 -> **replicates**
- L vs P (secondary), pass by checkpoint 500: 34/80 vs 8/80, difference +0.32, one-sided p = 0.0000 -> **L > P**

## Q2: predictors of a good start (L runs, pass by 500)

### Predictors, CEM runs (confirmatory; Holm over 5 at 0.05)

| feature | seen before? | pass rate, yes | pass rate, no | odds ratio | two-sided Fisher p | survives Holm |
|---|---|---|---|---|---|---|
| F1 pitch-to-hip gain sign correct (< 0) | no | 32/50 | 2/30 | 24.89 | 0.0000 | **yes** |
| F2 start held-out mean d >= 0.5 m | no | 11/14 | 23/66 | 6.86 | 0.0057 | **yes** |
| F3 hint level H2 (vs H0/H1) | yes | 24/40 | 10/40 | 4.50 | 0.0030 | **yes** |
| F4 model Opus (vs Sonnet) | yes | 20/40 | 14/40 | 1.86 | 0.2580 | no |
| F5 two or more oscillators | no | 1/2 | 33/78 | 1.36 | 1.0000 | no |

### Predictors, hill-climber runs (EXPLORATORY: F3/F4 counts were seen before this addendum)

| feature | seen before? | pass rate, yes | pass rate, no | odds ratio | two-sided Fisher p | survives Holm |
|---|---|---|---|---|---|---|
| F1 pitch-to-hip gain sign correct (< 0) | no | 35/50 | 4/30 | 15.17 | 0.0000 | **yes** |
| F2 start held-out mean d >= 0.5 m | no | 13/14 | 26/66 | 20.00 | 0.0003 | **yes** |
| F3 hint level H2 (vs H0/H1) | yes | 27/40 | 12/40 | 4.85 | 0.0016 | **yes** |
| F4 model Opus (vs Sonnet) | yes | 23/40 | 16/40 | 2.03 | 0.1793 | no |
| F5 two or more oscillators | no | 0/2 | 39/78 | 0.00 | 0.4940 | no |

## Per run (CEM)

- H `hand_s0`: T=None, d@500 1.82 m, 40.5 s
- H `hand_s1`: T=200, d@500 3.88 m, 55.9 s
- H `hand_s2`: T=None, d@500 2.82 m, 163.4 s
- H `hand_s3`: T=500, d@500 3.25 m, 60.6 s
- H `hand_s4`: T=100, d@500 3.96 m, 71.0 s
- H `hand_s5`: T=None, d@500 2.44 m, 55.7 s
- H `hand_s6`: T=200, d@500 3.64 m, 66.7 s
- H `hand_s7`: T=100, d@500 3.24 m, 56.3 s
- H `hand_s8`: T=200, d@500 4.18 m, 77.8 s
- H `hand_s9`: T=200, d@500 3.53 m, 59.4 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_00`: T=100, d@500 3.88 m, 53.2 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_01`: T=100, d@500 4.24 m, 96.9 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_02`: T=None, d@500 1.33 m, 201.5 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_03`: T=None, d@500 0.85 m, 30.1 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_04`: T=None, d@500 0.98 m, 34.0 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_05`: T=500, d@500 3.79 m, 133.9 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_06`: T=200, d@500 3.77 m, 69.9 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_07`: T=200, d@500 3.17 m, 49.3 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_08`: T=None, d@500 0.91 m, 26.5 s
- L `cpg-claude-opus-5-5_hopper_H0_cpgspec_09`: T=None, d@500 0.40 m, 36.9 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_00`: T=None, d@500 0.83 m, 32.0 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_01`: T=None, d@500 1.28 m, 37.3 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_02`: T=None, d@500 2.05 m, 33.8 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_03`: T=None, d@500 1.84 m, 39.7 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_04`: T=100, d@500 4.10 m, 84.3 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_05`: T=100, d@500 4.40 m, 75.9 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_06`: T=200, d@500 10.32 m, 158.9 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_07`: T=None, d@500 1.10 m, 26.4 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_08`: T=100, d@500 3.34 m, 109.4 s
- L `cpg-claude-opus-5-5_hopper_H1_cpgspec_09`: T=None, d@500 2.17 m, 43.5 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_00`: T=None, d@500 1.62 m, 41.7 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_01`: T=None, d@500 1.06 m, 34.4 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_02`: T=100, d@500 3.81 m, 55.4 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_03`: T=None, d@500 2.17 m, 115.6 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_04`: T=200, d@500 6.07 m, 98.5 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_05`: T=None, d@500 -0.01 m, 4.7 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_06`: T=None, d@500 2.60 m, 48.1 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_07`: T=200, d@500 5.07 m, 88.0 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_08`: T=None, d@500 1.41 m, 58.7 s
- L `cpg-claude-opus-5-5_hopper_H2_cpgspec_09`: T=500, d@500 3.51 m, 41.8 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_00`: T=None, d@500 0.80 m, 33.0 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_01`: T=None, d@500 0.20 m, 29.7 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_02`: T=None, d@500 0.09 m, 43.2 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_03`: T=None, d@500 1.36 m, 145.4 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_04`: T=None, d@500 0.84 m, 24.5 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_05`: T=None, d@500 1.15 m, 51.1 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_06`: T=None, d@500 1.02 m, 41.4 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_07`: T=None, d@500 0.37 m, 19.9 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_08`: T=None, d@500 0.12 m, 21.1 s
- L `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_09`: T=None, d@500 2.53 m, 63.5 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_00`: T=None, d@500 0.49 m, 34.5 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_01`: T=None, d@500 0.62 m, 24.8 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_02`: T=None, d@500 0.32 m, 37.3 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_03`: T=200, d@500 4.32 m, 83.1 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_04`: T=None, d@500 0.40 m, 22.9 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_05`: T=None, d@500 0.40 m, 32.2 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_06`: T=None, d@500 0.39 m, 23.6 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_07`: T=None, d@500 1.07 m, 37.9 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_08`: T=None, d@500 1.16 m, 35.1 s
- L `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_09`: T=None, d@500 0.36 m, 24.2 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_00`: T=None, d@500 1.67 m, 47.2 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_01`: T=200, d@500 4.35 m, 75.2 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_02`: T=200, d@500 3.79 m, 71.2 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_03`: T=200, d@500 3.87 m, 72.5 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_04`: T=200, d@500 3.15 m, 86.1 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_05`: T=None, d@500 1.38 m, 40.5 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_06`: T=None, d@500 0.25 m, 15.1 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_07`: T=100, d@500 4.43 m, 75.3 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_08`: T=100, d@500 3.42 m, 75.2 s
- L `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_09`: T=None, d@500 1.10 m, 43.3 s
- L `fb-claude-opus-5-5_hopper_H2_00`: T=None, d@500 1.11 m, 69.3 s
- L `fb-claude-opus-5-5_hopper_H2_01`: T=None, d@500 2.25 m, 52.4 s
- L `fb-claude-opus-5-5_hopper_H2_02`: T=100, d@500 3.87 m, 90.3 s
- L `fb-claude-opus-5-5_hopper_H2_03`: T=20, d@500 15.28 m, 245.0 s
- L `fb-claude-opus-5-5_hopper_H2_04`: T=100, d@500 4.47 m, 55.2 s
- L `fb-claude-opus-5-5_hopper_H2_05`: T=100, d@500 3.21 m, 55.1 s
- L `fb-claude-opus-5-5_hopper_H2_06`: T=100, d@500 4.42 m, 90.4 s
- L `fb-claude-opus-5-5_hopper_H2_07`: T=None, d@500 1.67 m, 105.5 s
- L `fb-claude-opus-5-5_hopper_H2_08`: T=200, d@500 3.86 m, 68.3 s
- L `fb-claude-opus-5-5_hopper_H2_09`: T=200, d@500 3.57 m, 64.1 s
- L `fb-claude-sonnet-5-5_hopper_H2_00`: T=200, d@500 3.79 m, 102.4 s
- L `fb-claude-sonnet-5-5_hopper_H2_01`: T=100, d@500 4.45 m, 89.6 s
- L `fb-claude-sonnet-5-5_hopper_H2_02`: T=200, d@500 3.36 m, 101.8 s
- L `fb-claude-sonnet-5-5_hopper_H2_03`: T=None, d@500 0.96 m, 65.5 s
- L `fb-claude-sonnet-5-5_hopper_H2_04`: T=100, d@500 3.82 m, 72.2 s
- L `fb-claude-sonnet-5-5_hopper_H2_05`: T=200, d@500 3.22 m, 94.3 s
- L `fb-claude-sonnet-5-5_hopper_H2_06`: T=None, d@500 1.75 m, 50.8 s
- L `fb-claude-sonnet-5-5_hopper_H2_07`: T=100, d@500 3.15 m, 89.0 s
- L `fb-claude-sonnet-5-5_hopper_H2_08`: T=None, d@500 1.56 m, 48.9 s
- L `fb-claude-sonnet-5-5_hopper_H2_09`: T=500, d@500 3.06 m, 85.5 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_00__perm`: T=None, d@500 0.74 m, 25.8 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_01__perm`: T=None, d@500 0.97 m, 39.3 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_02__perm`: T=None, d@500 0.76 m, 26.2 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_03__perm`: T=None, d@500 2.38 m, 28.1 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_04__perm`: T=None, d@500 -0.01 m, 4.0 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_05__perm`: T=None, d@500 0.95 m, 30.5 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_06__perm`: T=None, d@500 2.27 m, 59.5 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_07__perm`: T=None, d@500 -0.01 m, 5.3 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_08__perm`: T=None, d@500 0.96 m, 47.0 s
- P `cpg-claude-opus-5-5_hopper_H0_cpgspec_09__perm`: T=None, d@500 1.95 m, 43.3 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_00__perm`: T=200, d@500 4.48 m, 63.9 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_01__perm`: T=None, d@500 0.22 m, 12.0 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_02__perm`: T=None, d@500 1.02 m, 31.3 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_03__perm`: T=None, d@500 1.71 m, 81.9 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_04__perm`: T=None, d@500 1.44 m, 34.5 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_05__perm`: T=None, d@500 0.43 m, 19.7 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_06__perm`: T=None, d@500 0.96 m, 48.5 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_07__perm`: T=None, d@500 -0.01 m, 4.3 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_08__perm`: T=100, d@500 3.25 m, 42.9 s
- P `cpg-claude-opus-5-5_hopper_H1_cpgspec_09__perm`: T=100, d@500 4.98 m, 73.5 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_00__perm`: T=None, d@500 0.74 m, 47.7 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_01__perm`: T=None, d@500 0.20 m, 11.2 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_02__perm`: T=500, d@500 3.23 m, 118.5 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_03__perm`: T=None, d@500 1.93 m, 33.2 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_04__perm`: T=None, d@500 1.18 m, 40.1 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_05__perm`: T=None, d@500 -0.01 m, 3.7 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_06__perm`: T=None, d@500 -0.02 m, 3.3 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_07__perm`: T=None, d@500 1.18 m, 26.0 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_08__perm`: T=None, d@500 0.99 m, 32.8 s
- P `cpg-claude-opus-5-5_hopper_H2_cpgspec_09__perm`: T=None, d@500 0.96 m, 38.0 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_00__perm`: T=None, d@500 2.44 m, 57.1 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_01__perm`: T=None, d@500 0.07 m, 14.1 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_02__perm`: T=None, d@500 0.10 m, 54.4 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_03__perm`: T=None, d@500 -0.01 m, 7.4 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_04__perm`: T=None, d@500 1.07 m, 40.7 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_05__perm`: T=None, d@500 2.95 m, 59.9 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_06__perm`: T=None, d@500 0.69 m, 17.4 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_07__perm`: T=None, d@500 -0.01 m, 4.7 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_08__perm`: T=None, d@500 0.87 m, 34.3 s
- P `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_09__perm`: T=None, d@500 0.97 m, 49.9 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_00__perm`: T=None, d@500 0.91 m, 30.3 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_01__perm`: T=None, d@500 1.86 m, 55.6 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_02__perm`: T=None, d@500 -0.11 m, 6.0 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_03__perm`: T=None, d@500 -0.01 m, 3.9 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_04__perm`: T=None, d@500 0.26 m, 30.7 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_05__perm`: T=None, d@500 1.30 m, 38.9 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_06__perm`: T=None, d@500 0.92 m, 28.9 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_07__perm`: T=None, d@500 -0.01 m, 5.9 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_08__perm`: T=None, d@500 0.97 m, 31.2 s
- P `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_09__perm`: T=None, d@500 0.97 m, 24.9 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_00__perm`: T=None, d@500 -0.01 m, 7.3 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_01__perm`: T=None, d@500 0.46 m, 17.2 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_02__perm`: T=100, d@500 3.51 m, 67.2 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_03__perm`: T=None, d@500 0.78 m, 42.2 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_04__perm`: T=None, d@500 1.08 m, 26.3 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_05__perm`: T=100, d@500 3.94 m, 80.9 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_06__perm`: T=None, d@500 0.09 m, 14.6 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_07__perm`: T=None, d@500 0.76 m, 34.7 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_08__perm`: T=None, d@500 0.71 m, 29.6 s
- P `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_09__perm`: T=200, d@500 3.37 m, 92.1 s
- P `fb-claude-opus-5-5_hopper_H2_00__perm`: T=None, d@500 1.16 m, 43.0 s
- P `fb-claude-opus-5-5_hopper_H2_01__perm`: T=None, d@500 -0.01 m, 5.3 s
- P `fb-claude-opus-5-5_hopper_H2_02__perm`: T=None, d@500 -0.01 m, 6.0 s
- P `fb-claude-opus-5-5_hopper_H2_03__perm`: T=None, d@500 0.28 m, 14.1 s
- P `fb-claude-opus-5-5_hopper_H2_04__perm`: T=None, d@500 0.93 m, 35.9 s
- P `fb-claude-opus-5-5_hopper_H2_05__perm`: T=None, d@500 1.41 m, 32.1 s
- P `fb-claude-opus-5-5_hopper_H2_06__perm`: T=None, d@500 0.97 m, 41.6 s
- P `fb-claude-opus-5-5_hopper_H2_07__perm`: T=None, d@500 0.74 m, 35.7 s
- P `fb-claude-opus-5-5_hopper_H2_08__perm`: T=None, d@500 2.04 m, 40.1 s
- P `fb-claude-opus-5-5_hopper_H2_09__perm`: T=None, d@500 0.89 m, 45.0 s
- P `fb-claude-sonnet-5-5_hopper_H2_00__perm`: T=None, d@500 0.53 m, 27.9 s
- P `fb-claude-sonnet-5-5_hopper_H2_01__perm`: T=100, d@500 4.34 m, 83.7 s
- P `fb-claude-sonnet-5-5_hopper_H2_02__perm`: T=None, d@500 0.20 m, 19.5 s
- P `fb-claude-sonnet-5-5_hopper_H2_03__perm`: T=None, d@500 0.99 m, 59.5 s
- P `fb-claude-sonnet-5-5_hopper_H2_04__perm`: T=None, d@500 -0.10 m, 11.2 s
- P `fb-claude-sonnet-5-5_hopper_H2_05__perm`: T=None, d@500 0.45 m, 24.8 s
- P `fb-claude-sonnet-5-5_hopper_H2_06__perm`: T=None, d@500 -0.01 m, 4.3 s
- P `fb-claude-sonnet-5-5_hopper_H2_07__perm`: T=None, d@500 1.81 m, 57.6 s
- P `fb-claude-sonnet-5-5_hopper_H2_08__perm`: T=None, d@500 1.77 m, 42.1 s
- P `fb-claude-sonnet-5-5_hopper_H2_09__perm`: T=None, d@500 0.98 m, 36.0 s
- R `rand1000`: T=None, d@500 0.62 m, 17.9 s
- R `rand1001`: T=None, d@500 0.71 m, 18.7 s
- R `rand1002`: T=None, d@500 0.82 m, 35.3 s
- R `rand1003`: T=None, d@500 0.30 m, 13.1 s
- R `rand1004`: T=None, d@500 0.74 m, 24.1 s
- R `rand1005`: T=None, d@500 0.61 m, 22.1 s
- R `rand1006`: T=None, d@500 0.22 m, 10.9 s
- R `rand1007`: T=None, d@500 0.43 m, 16.7 s
- R `rand1008`: T=None, d@500 1.78 m, 55.3 s
- R `rand1009`: T=None, d@500 0.51 m, 20.9 s
- R `rand1010`: T=None, d@500 -0.01 m, 4.0 s
- R `rand1011`: T=None, d@500 0.00 m, 4.8 s
- R `rand1012`: T=None, d@500 -0.01 m, 3.8 s
- R `rand1013`: T=None, d@500 1.40 m, 35.2 s
- R `rand1014`: T=None, d@500 0.36 m, 16.4 s
- R `rand1015`: T=None, d@500 0.95 m, 22.9 s
- R `rand1016`: T=None, d@500 0.31 m, 13.6 s
- R `rand1017`: T=None, d@500 0.47 m, 19.0 s
- R `rand1018`: T=None, d@500 0.25 m, 12.7 s
- R `rand1019`: T=None, d@500 0.50 m, 13.0 s
- R `rand1020`: T=None, d@500 0.99 m, 29.8 s
- R `rand1021`: T=None, d@500 0.43 m, 18.9 s
- R `rand1022`: T=None, d@500 2.00 m, 52.6 s
- R `rand1023`: T=None, d@500 0.72 m, 25.8 s
- R `rand1024`: T=None, d@500 0.81 m, 22.3 s
- R `rand1025`: T=None, d@500 0.64 m, 16.1 s
- R `rand1026`: T=None, d@500 0.94 m, 30.5 s
- R `rand1027`: T=None, d@500 0.31 m, 13.9 s
- R `rand1028`: T=None, d@500 0.36 m, 13.1 s
- R `rand1029`: T=None, d@500 0.20 m, 11.3 s
- R `rand1030`: T=None, d@500 0.94 m, 22.2 s
- R `rand1031`: T=None, d@500 -0.01 m, 4.0 s
- R `rand1032`: T=None, d@500 0.47 m, 20.5 s
- R `rand1033`: T=None, d@500 0.22 m, 10.8 s
- R `rand1034`: T=None, d@500 0.84 m, 25.9 s
- R `rand1035`: T=None, d@500 0.26 m, 12.4 s
- R `rand1036`: T=None, d@500 0.31 m, 17.3 s
- R `rand1037`: T=None, d@500 1.28 m, 28.3 s
- R `rand1038`: T=None, d@500 0.73 m, 31.8 s
- R `rand1039`: T=None, d@500 0.87 m, 23.3 s
- R `rand1040`: T=None, d@500 0.94 m, 25.8 s
- R `rand1041`: T=None, d@500 0.46 m, 19.6 s
- R `rand1042`: T=200, d@500 3.22 m, 74.7 s
- R `rand1043`: T=None, d@500 0.23 m, 5.3 s
- R `rand1044`: T=None, d@500 0.45 m, 22.5 s
- R `rand1045`: T=None, d@500 0.81 m, 28.6 s
- R `rand1046`: T=None, d@500 1.28 m, 24.9 s
- R `rand1047`: T=None, d@500 0.65 m, 19.9 s
- R `rand1048`: T=None, d@500 1.57 m, 24.8 s
- R `rand1049`: T=None, d@500 0.55 m, 20.9 s
- R `rand1050`: T=None, d@500 0.29 m, 14.3 s
- R `rand1051`: T=None, d@500 0.32 m, 17.2 s
- R `rand1052`: T=None, d@500 1.89 m, 39.7 s
- R `rand1053`: T=None, d@500 0.50 m, 20.4 s
- R `rand1054`: T=200, d@500 3.27 m, 68.4 s
- R `rand1055`: T=None, d@500 0.61 m, 30.4 s
- R `rand1056`: T=None, d@500 0.18 m, 12.5 s
- R `rand1057`: T=None, d@500 0.57 m, 17.6 s
- R `rand1058`: T=None, d@500 2.11 m, 49.6 s
- R `rand1059`: T=None, d@500 0.47 m, 21.8 s
- R `rand1060`: T=None, d@500 0.76 m, 25.5 s
- R `rand1061`: T=None, d@500 0.70 m, 22.3 s
- R `rand1062`: T=None, d@500 1.36 m, 26.4 s
- R `rand1063`: T=None, d@500 0.88 m, 32.4 s
- R `rand1064`: T=None, d@500 0.95 m, 27.7 s
- R `rand1065`: T=None, d@500 0.42 m, 19.2 s
- R `rand1066`: T=None, d@500 0.12 m, 10.5 s
- R `rand1067`: T=None, d@500 -0.01 m, 4.8 s
- R `rand1068`: T=None, d@500 0.68 m, 28.2 s
- R `rand1069`: T=None, d@500 0.29 m, 17.5 s
- R `rand1070`: T=None, d@500 0.39 m, 20.9 s
- R `rand1071`: T=None, d@500 0.27 m, 18.9 s
- R `rand1072`: T=None, d@500 0.84 m, 27.6 s
- R `rand1073`: T=None, d@500 0.71 m, 31.7 s
- R `rand1074`: T=None, d@500 0.26 m, 17.5 s
- R `rand1075`: T=None, d@500 0.94 m, 34.8 s
- R `rand1076`: T=None, d@500 0.38 m, 20.7 s
- R `rand1077`: T=None, d@500 0.75 m, 27.4 s
- R `rand1078`: T=None, d@500 0.79 m, 22.1 s
- R `rand1079`: T=None, d@500 0.26 m, 18.9 s
