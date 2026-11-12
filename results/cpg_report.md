# CPG track report (local; numbers stay in results/)

Prereg: docs/prereg-2026-11-09-cpg.md. d = forward displacement to the last healthy step, 100 scoring episodes (seeds 10000..10099). Attempt passes: mean d >= 3 m and >= 50 clean episodes. Arm meets the target: >= 5 of 10 attempts pass. Simulation only (MuJoCo through Gymnasium); one reply per attempt, no execution, no training.

### hopper: necessity table and CPG baselines

| row | mean d (m) | median d | min d | clean eps (>=3 m) | passes | mean return | full-length frac | note |
|---|---|---|---|---|---|---|---|---|
| zero weights | -0.01 | -0.04 | -0.11 | 0 | no | 148 | 0.00 |  |
| random MLP (n=10) | median -0.02, max 0.19 | | | 0 | 0 pass | | | 10 seeds |
| stand-still (highest-return earlier attempt) | 0.59 | 0.59 | 0.58 | 0 | no | 1074 | 1.00 | claude-opus-5-5_hopper_named_controller_02_iso2 |
| fall-forward lunge (best constant action, dev seeds) | 0.74 | 0.74 | 0.70 | 0 | no | 200 | 0.00 |  |
| open-loop sinusoid (tuned on dev seeds) | 0.46 | 0.46 | 0.44 | 0 | no | 130 | 0.00 | 9650 dev episodes |
| random CPG (n=50) | median -0.02, best 0.35 | | | 0 | 0 pass | | | necessity: median < 1.5 m: holds |
| tuned CPG (headroom; search on dev seeds) | 3.27 | 3.18 | 1.72 | 80 | yes | 787 | 0.00 | 19650 dev episodes |
| PPO hopper_ppo_seed0.score (upper reference, env reward) | 12.66 | 12.68 | 6.88 | 100 | yes | 2191 | 0.09 |  |
| PPO hopper_ppo_seed1.score (upper reference, env reward) | 17.48 | 20.01 | 6.69 | 100 | yes | 3054 | 0.75 |  |
| PPO hopper_ppo_seed2.score (upper reference, env reward) | 13.90 | 14.45 | 7.20 | 100 | yes | 2461 | 0.27 |  |

Necessity rule (each simple baseline mean d < 1.5 m): zero: holds, lunge: holds, sinusoid: holds

### hopper: LLM attempts (mode cpgspec)

| model | level | n | failures | passes (target: >= 5 of 10) | mean d | median d | best d | bins <0 / 0-0.5 / 0.5-1.5 / 1.5-3 / 3-5 / >=5 | pitch->hip gain < 0 (post hoc) |
|---|---|---|---|---|---|---|---|---|---|
| claude-opus-5-5 | H2 | 10 | 0 | 0 | 0.03 | -0.04 | 1.07 | 9 / 0 / 1 / 0 / 0 / 0 | 7 of 10 |
| claude-opus-5-5 | H1 | 10 | 0 | 0 | 0.03 | 0.01 | 0.22 | 4 / 6 / 0 / 0 / 0 / 0 | 4 of 10 |
| claude-opus-5-5 | H0 | 10 | 0 | 0 | 0.17 | 0.09 | 1.08 | 4 / 5 / 1 / 0 / 0 / 0 | 5 of 10 |
| claude-sonnet-5-5 | H2 | 10 | 0 | 0 | 0.35 | 0.20 | 0.94 | 2 / 5 / 3 / 0 / 0 / 0 | 10 of 10 |
| claude-sonnet-5-5 | H1 | 10 | 0 | 0 | 0.17 | 0.08 | 0.92 | 2 / 7 / 1 / 0 / 0 / 0 | 1 of 10 |
| claude-sonnet-5-5 | H0 | 10 | 0 | 0 | 0.09 | -0.02 | 0.94 | 7 / 2 / 1 / 0 / 0 / 0 | 3 of 10 |

Per attempt (id: mean d to last healthy step, clean episodes, or failure):

- `cpg-claude-opus-5-5_hopper_H0_cpgspec_00`: 0.24 m, 0 clean, return 1030, full-length 1.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_01`: 0.17 m, 0 clean, return 1021, full-length 1.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_02`: 0.00 m, 0 clean, return 16, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_03`: -0.03 m, 0 clean, return 5, full-length 0.00, pitch->hip gain 1.2
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_04`: -0.08 m, 0 clean, return 30, full-length 0.00, pitch->hip gain -7.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_05`: -0.03 m, 0 clean, return 12, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_06`: 1.08 m, 0 clean, return 377, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_07`: -0.02 m, 0 clean, return 10, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_08`: 0.18 m, 0 clean, return 62, full-length 0.00, pitch->hip gain 1.8
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_09`: 0.22 m, 0 clean, return 112, full-length 0.00, pitch->hip gain 1.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_00`: 0.22 m, 0 clean, return 74, full-length 0.00, pitch->hip gain 1.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_01`: -0.02 m, 0 clean, return 8, full-length 0.00, pitch->hip gain 1.2
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_02`: -0.08 m, 0 clean, return 35, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_03`: -0.03 m, 0 clean, return 10, full-length 0.00, pitch->hip gain 1.4
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_04`: 0.08 m, 0 clean, return 1010, full-length 1.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_05`: 0.05 m, 0 clean, return 38, full-length 0.00, pitch->hip gain -1.5
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_06`: 0.02 m, 0 clean, return 26, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_07`: -0.02 m, 0 clean, return 5, full-length 0.00, pitch->hip gain 2.5
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_08`: 0.00 m, 0 clean, return 21, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_09`: 0.08 m, 0 clean, return 40, full-length 0.00, pitch->hip gain 0.8
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_00`: -0.06 m, 0 clean, return 10, full-length 0.00, pitch->hip gain 0.5
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_01`: -0.02 m, 0 clean, return 11, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_02`: -0.21 m, 0 clean, return 204, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_03`: -0.00 m, 0 clean, return 29, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_04`: -0.05 m, 0 clean, return 74, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_05`: -0.17 m, 0 clean, return 10, full-length 0.00, pitch->hip gain -2.5
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_06`: -0.03 m, 0 clean, return 7, full-length 0.00, pitch->hip gain -2.5
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_07`: -0.03 m, 0 clean, return 20, full-length 0.00, pitch->hip gain 1.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_08`: 1.07 m, 0 clean, return 287, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_09`: -0.22 m, 0 clean, return 7, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_00`: 0.25 m, 0 clean, return 84, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_01`: -0.02 m, 0 clean, return 28, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_02`: -0.03 m, 0 clean, return 28, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_03`: -0.00 m, 0 clean, return 999, full-length 1.00, pitch->hip gain -5.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_04`: -0.12 m, 0 clean, return 7, full-length 0.00, pitch->hip gain 0.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_05`: 0.00 m, 0 clean, return 41, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_06`: -0.05 m, 0 clean, return 11, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_07`: -0.07 m, 0 clean, return 11, full-length 0.00, pitch->hip gain 1.2
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_08`: -0.02 m, 0 clean, return 20, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_09`: 0.94 m, 0 clean, return 244, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_00`: 0.05 m, 0 clean, return 30, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_01`: 0.03 m, 0 clean, return 26, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_02`: 0.17 m, 0 clean, return 56, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_03`: 0.92 m, 0 clean, return 228, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_04`: 0.10 m, 0 clean, return 55, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_05`: 0.07 m, 0 clean, return 38, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_06`: -0.01 m, 0 clean, return 6, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_07`: -0.01 m, 0 clean, return 5, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_08`: 0.19 m, 0 clean, return 78, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_09`: 0.18 m, 0 clean, return 68, full-length 0.00, pitch->hip gain 5.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_00`: 0.04 m, 0 clean, return 37, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_01`: 0.24 m, 0 clean, return 88, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_02`: 0.94 m, 0 clean, return 234, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_03`: 0.22 m, 0 clean, return 82, full-length 0.00, pitch->hip gain -6.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_04`: 0.93 m, 0 clean, return 227, full-length 0.00, pitch->hip gain -5.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_05`: 0.15 m, 0 clean, return 75, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_06`: -0.06 m, 0 clean, return 6, full-length 0.00, pitch->hip gain -1.5
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_07`: 0.17 m, 0 clean, return 70, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_08`: 0.93 m, 0 clean, return 230, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-sonnet-5-5_hopper_H2_cpgspec_09`: -0.06 m, 0 clean, return 6, full-length 0.00, pitch->hip gain -4.0

Transport failures, repeated once with the same index (prereg s6; kept, see NOTE.md in each): `cpg-claude-opus-5-5_hopper_H0_cpgspec_01_try1`

### walker2d: necessity table and CPG baselines

| row | mean d (m) | median d | min d | clean eps (>=3 m) | passes | mean return | full-length frac | note |
|---|---|---|---|---|---|---|---|---|
| zero weights | -0.17 | -0.16 | -0.87 | 0 | no | 96 | 0.00 |  |
| random MLP (n=10) | median -0.19, max -0.08 | | | 0 | 0 pass | | | 10 seeds |
| fall-forward lunge (best constant action, dev seeds) | 0.96 | 0.96 | 0.94 | 0 | no | 350 | 0.00 |  |
| open-loop sinusoid (tuned on dev seeds) | -0.05 | -0.05 | -0.05 | 0 | no | -3 | 0.00 | 9650 dev episodes |
| random CPG (n=50) | median -0.16, best -0.06 | | | 0 | 0 pass | | | necessity: median < 1.5 m: holds |
| tuned CPG (headroom; search on dev seeds) | 1.29 | 1.29 | 1.19 | 0 | no | 382 | 0.00 | 19650 dev episodes |
| PPO walker2d_ppo_seed0.score (upper reference, env reward) | 16.57 | 18.18 | 4.94 | 100 | yes | 2974 | 0.79 |  |
| PPO walker2d_ppo_seed1.score (upper reference, env reward) | 6.97 | 5.58 | 2.31 | 99 | yes | 1429 | 0.04 |  |
| PPO walker2d_ppo_seed2.score (upper reference, env reward) | 3.75 | 3.75 | 3.67 | 100 | yes | 717 | 0.00 |  |

Necessity rule (each simple baseline mean d < 1.5 m): zero: holds, lunge: holds, sinusoid: holds

### walker2d: LLM attempts (mode cpgspec)

| model | level | n | failures | passes (target: >= 5 of 10) | mean d | median d | best d | bins <0 / 0-0.5 / 0.5-1.5 / 1.5-3 / 3-5 / >=5 | pitch->hip gain < 0 (post hoc) |
|---|---|---|---|---|---|---|---|---|---|
| claude-opus-5-5 | H2 | 10 | 0 | 0 | -0.07 | -0.10 | 1.08 | 6 / 0 / 4 / 0 / 0 / 0 | 8 of 10 |
| claude-opus-5-5 | H1 | 10 | 0 | 0 | -0.26 | -0.10 | 1.30 | 8 / 0 / 2 / 0 / 0 / 0 | 3 of 10 |
| claude-opus-5-5 | H0 | 10 | 0 | 0 | -0.09 | -0.07 | -0.06 | 10 / 0 / 0 / 0 / 0 / 0 | 0 of 10 |
| claude-sonnet-5-5 | H2 | 10 | 0 | 0 | -0.16 | -0.02 | 0.10 | 7 / 3 / 0 / 0 / 0 / 0 | 10 of 10 |
| claude-sonnet-5-5 | H1 | 10 | 0 | 0 | -0.15 | -0.07 | -0.06 | 10 / 0 / 0 / 0 / 0 / 0 | 1 of 10 |
| claude-sonnet-5-5 | H0 | 10 | 0 | 0 | -0.35 | -0.07 | -0.07 | 10 / 0 / 0 / 0 / 0 / 0 | 3 of 10 |

Per attempt (id: mean d to last healthy step, clean episodes, or failure):

- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_00`: -0.06 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 1.6
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_01`: -0.07 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_02`: -0.11 m, 0 clean, return 8, full-length 0.00, pitch->hip gain 9.6
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_03`: -0.08 m, 0 clean, return -6, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_04`: -0.06 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 1.62
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_05`: -0.18 m, 0 clean, return 18, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_06`: -0.08 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 1.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_07`: -0.10 m, 0 clean, return 12, full-length 0.00, pitch->hip gain 1.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_08`: -0.07 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_walker2d_H0_cpgspec_09`: -0.07 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 1.6
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_00`: -0.08 m, 0 clean, return -5, full-length 0.00, pitch->hip gain 1.4
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_01`: 1.30 m, 0 clean, return 458, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_02`: -0.10 m, 0 clean, return 2, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_03`: -0.10 m, 0 clean, return -5, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_04`: -2.23 m, 0 clean, return 123, full-length 0.13, pitch->hip gain 6.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_05`: -0.10 m, 0 clean, return -2, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_06`: -0.08 m, 0 clean, return -2, full-length 0.00, pitch->hip gain 7.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_07`: 0.93 m, 0 clean, return 324, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_08`: -0.88 m, 0 clean, return -31, full-length 0.00, pitch->hip gain -6.0
- `cpg-claude-opus-5-5_walker2d_H1_cpgspec_09`: -1.29 m, 0 clean, return 45, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_00`: -0.85 m, 0 clean, return 59, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_01`: 1.08 m, 0 clean, return 406, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_02`: -1.16 m, 0 clean, return 141, full-length 0.03, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_03`: 0.90 m, 0 clean, return 279, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_04`: 0.50 m, 0 clean, return 419, full-length 0.00, pitch->hip gain -1.6
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_05`: -1.64 m, 0 clean, return 98, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_06`: 0.90 m, 0 clean, return 285, full-length 0.00, pitch->hip gain -1.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_07`: -0.10 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 6.0
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_08`: -0.24 m, 0 clean, return 296, full-length 0.00, pitch->hip gain -1.6
- `cpg-claude-opus-5-5_walker2d_H2_cpgspec_09`: -0.10 m, 0 clean, return 9, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_00`: -0.26 m, 0 clean, return -18, full-length 0.00, pitch->hip gain 0.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_01`: -0.07 m, 0 clean, return 3, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_02`: -0.95 m, 0 clean, return 124, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_03`: -0.07 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_04`: -0.07 m, 0 clean, return -0, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_05`: -0.07 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 6.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_06`: -0.07 m, 0 clean, return -2, full-length 0.00, pitch->hip gain 6.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_07`: -0.07 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_08`: -0.93 m, 0 clean, return 123, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_walker2d_H0_cpgspec_09`: -0.93 m, 0 clean, return 95, full-length 0.00, pitch->hip gain -6.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_00`: -0.07 m, 0 clean, return -1, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_01`: -0.07 m, 0 clean, return 1, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_02`: -0.07 m, 0 clean, return -5, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_03`: -0.07 m, 0 clean, return -2, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_04`: -0.07 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_05`: -0.88 m, 0 clean, return 13, full-length 0.00, pitch->hip gain -1.6
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_06`: -0.06 m, 0 clean, return -4, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_07`: -0.08 m, 0 clean, return -5, full-length 0.00, pitch->hip gain 3.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_08`: -0.07 m, 0 clean, return -2, full-length 0.00, pitch->hip gain 4.0
- `cpg-claude-sonnet-5-5_walker2d_H1_cpgspec_09`: -0.07 m, 0 clean, return -3, full-length 0.00, pitch->hip gain 2.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_00`: 0.10 m, 0 clean, return 107, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_01`: -0.47 m, 0 clean, return 58, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_02`: 0.03 m, 0 clean, return 115, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_03`: -0.03 m, 0 clean, return 67, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_04`: -0.56 m, 0 clean, return -1, full-length 0.00, pitch->hip gain -4.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_05`: -0.55 m, 0 clean, return 37, full-length 0.00, pitch->hip gain -3.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_06`: -0.00 m, 0 clean, return 73, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_07`: -0.00 m, 0 clean, return 102, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_08`: 0.03 m, 0 clean, return 101, full-length 0.00, pitch->hip gain -2.0
- `cpg-claude-sonnet-5-5_walker2d_H2_cpgspec_09`: -0.14 m, 0 clean, return 75, full-length 0.00, pitch->hip gain -2.0

Transport failures, repeated once with the same index (prereg s6; kept, see NOTE.md in each): `cpg-claude-opus-5-5_walker2d_H2_cpgspec_00_aborted1`

## Verdict (prereg section 8)

- hopper: **did not work**: no arm meets the target (all 6 Claude cells complete, 10 attempts each).
- walker2d: **did not work**: no arm meets the target (all 6 Claude cells complete, 10 attempts each).
