# CPG feedback arm report (local; numbers stay in results/)

Prereg: docs/prereg-2026-11-10-cpg-feedback.md. Level H2. 6 designs per attempt (round 0 + 5 revisions) from a fixed dev-seed summary (seeds 0..9); primary = round-5 design, scored on held-out seeds 10000..10099. Pass: mean d >= 3 m and >= 50 clean episodes; arm meets the target with >= 5 of 10 passing attempts. Simulation only.

## hopper

| arm | n | passes | mean d (m) | median d | best d | attempts >= 1.5 m |
|---|---|---|---|---|---|---|
| feedback, claude-opus-5-5, round 5 (primary) | 10 | 2 | 1.92 | 1.27 | 6.90 | 4 |
| feedback, claude-opus-5-5, round 0 (its own no-feedback control) | 10 | 1 | 0.62 | -0.11 | 6.12 | 1 |
| no-feedback arm (track, H2), claude-opus-5-5 | 10 | 0 | 0.03 | -0.04 | 1.07 | 0 |
| RS-from-LLM (start = claude-opus-5-5 round 0) | 10 | 1 | 0.86 | 0.09 | 6.12 | 2 |
| feedback, claude-sonnet-5-5, round 5 (primary) | 10 | 0 | 0.76 | 0.94 | 0.96 | 0 |
| feedback, claude-sonnet-5-5, round 0 (its own no-feedback control) | 10 | 0 | 0.43 | 0.38 | 0.96 | 0 |
| no-feedback arm (track, H2), claude-sonnet-5-5 | 10 | 0 | 0.35 | 0.20 | 0.94 | 0 |
| RS-from-LLM (start = claude-sonnet-5-5 round 0) | 10 | 0 | 0.74 | 0.62 | 2.67 | 1 |
| RS-random (random CPG start) | 10 | 0 | 0.11 | 0.05 | 0.48 | 0 |

Held-out mean d by round (median over attempts; never shown to the model):

| model | r0 | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|---|
| claude-opus-5-5 | -0.11 | 0.03 | 0.09 | 0.83 | 0.02 | 1.27 |
| claude-sonnet-5-5 | 0.38 | 0.92 | 0.24 | 0.59 | 0.70 | 0.94 |

Per attempt (held-out mean d per round r0..r5; dev mean d per round in brackets):

- `fb-claude-opus-5-5_hopper_H2_00`: -0.16 [-0.16], 0.03 [0.03], 0.02 [0.02], 0.20 [0.20], -0.02 [-0.02], -0.04 [-0.04]
- `fb-claude-opus-5-5_hopper_H2_01`: 1.11 [1.11], -0.10 [-0.10], 0.01 [0.01], 0.09 [0.09], 1.18 [1.20], 1.07 [1.06]
- `fb-claude-opus-5-5_hopper_H2_02`: -0.18 [-0.18], -0.01 [-0.01], 0.15 [0.15], 1.49 [1.48], 0.00 [0.00], 1.47 [1.48]
- `fb-claude-opus-5-5_hopper_H2_03`: 6.12 [6.14], 4.73 [4.63], 4.96 [4.97], 6.42 [6.33], 5.55 [5.41], 6.42 [6.33] PASS
- `fb-claude-opus-5-5_hopper_H2_04`: -0.04 [-0.04], 0.08 [0.08], 1.53 [1.53], 1.48 [1.48], 0.76 [0.49], 1.53 [1.53]
- `fb-claude-opus-5-5_hopper_H2_05`: -0.21 [-0.21], 0.03 [0.03], 0.01 [0.01], -0.05 [-0.05], -0.04 [-0.04], 0.17 [0.17]
- `fb-claude-opus-5-5_hopper_H2_06`: -0.04 [-0.04], -0.14 [-0.14], 1.50 [1.50], 1.46 [1.46], -0.04 [-0.04], 1.50 [1.50]
- `fb-claude-opus-5-5_hopper_H2_07`: -0.18 [-0.18], 0.07 [0.07], -0.03 [-0.03], 0.16 [0.16], -0.00 [-0.03], 0.18 [0.18]
- `fb-claude-opus-5-5_hopper_H2_08`: -0.06 [-0.06], 0.13 [0.13], 5.43 [5.43], 6.32 [6.32], 6.90 [6.90], 6.90 [6.90] PASS
- `fb-claude-opus-5-5_hopper_H2_09`: -0.16 [-0.16], -0.01 [-0.00], -0.04 [-0.04], -0.08 [-0.08], 0.04 [0.04], -0.05 [-0.05]
- `fb-claude-sonnet-5-5_hopper_H2_00`: 0.96 [0.96], 0.92 [0.92], -0.01 [-0.01], -0.08 [-0.08], -0.05 [-0.06], 0.96 [0.96]
- `fb-claude-sonnet-5-5_hopper_H2_01`: 0.86 [0.85], 0.92 [0.92], 0.17 [0.17], 0.51 [0.51], 0.85 [0.85], 0.95 [0.95]
- `fb-claude-sonnet-5-5_hopper_H2_02`: 0.05 [0.05], 0.01 [0.01], 0.91 [0.91], 0.93 [0.93], -0.02 [-0.02], 0.93 [0.93]
- `fb-claude-sonnet-5-5_hopper_H2_03`: -0.21 [-0.21], -0.00 [-0.00], -0.02 [-0.02], -0.02 [-0.02], 0.92 [0.92], 0.27 [0.61]
- `fb-claude-sonnet-5-5_hopper_H2_04`: 0.89 [0.88], 0.97 [0.96], 0.32 [0.29], 0.76 [0.70], 0.94 [0.94], 0.95 [0.95]
- `fb-claude-sonnet-5-5_hopper_H2_05`: 0.52 [0.66], 0.93 [0.94], 0.33 [0.33], 0.84 [0.84], 0.14 [0.14], 0.78 [0.68]
- `fb-claude-sonnet-5-5_hopper_H2_06`: 0.05 [0.05], 0.02 [0.02], -0.08 [-0.08], -0.02 [-0.02], -0.16 [-0.16], -0.05 [-0.05]
- `fb-claude-sonnet-5-5_hopper_H2_07`: 0.94 [0.94], 0.93 [0.93], 0.45 [0.45], 0.67 [0.67], 0.56 [0.56], 0.95 [0.95]
- `fb-claude-sonnet-5-5_hopper_H2_08`: 0.04 [0.04], 0.04 [0.04], -0.03 [-0.02], -0.08 [-0.07], 0.93 [0.93], 0.93 [0.93]
- `fb-claude-sonnet-5-5_hopper_H2_09`: 0.23 [0.23], 0.96 [0.96], 0.92 [0.92], 0.73 [0.73], 0.94 [0.94], 0.95 [0.94]

## walker2d

| arm | n | passes | mean d (m) | median d | best d | attempts >= 1.5 m |
|---|---|---|---|---|---|---|
| feedback, claude-opus-5-5, round 5 (primary) | 10 | 0 | -1.32 | -1.10 | 0.83 | 0 |
| feedback, claude-opus-5-5, round 0 (its own no-feedback control) | 10 | 0 | -0.73 | -0.81 | -0.07 | 0 |
| no-feedback arm (track, H2), claude-opus-5-5 | 10 | 0 | -0.07 | -0.10 | 1.08 | 0 |
| RS-from-LLM (start = claude-opus-5-5 round 0) | 10 | 0 | 0.17 | -0.07 | 1.00 | 0 |
| feedback, claude-sonnet-5-5, round 5 (primary) | 10 | 0 | 0.35 | 0.68 | 0.97 | 0 |
| feedback, claude-sonnet-5-5, round 0 (its own no-feedback control) | 10 | 0 | -0.01 | -0.04 | 0.14 | 0 |
| no-feedback arm (track, H2), claude-sonnet-5-5 | 10 | 0 | -0.16 | -0.02 | 0.10 | 0 |
| RS-from-LLM (start = claude-sonnet-5-5 round 0) | 10 | 0 | 0.09 | 0.03 | 0.88 | 0 |
| RS-random (random CPG start) | 10 | 0 | -0.08 | -0.07 | -0.06 | 0 |

Held-out mean d by round (median over attempts; never shown to the model):

| model | r0 | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|---|
| claude-opus-5-5 | -0.81 | -0.89 | -1.06 | -1.08 | -1.13 | -1.10 |
| claude-sonnet-5-5 | -0.04 | -0.83 | -0.14 | 0.38 | 0.38 | 0.68 |

Per attempt (held-out mean d per round r0..r5; dev mean d per round in brackets):

- `fb-claude-opus-5-5_walker2d_H2_00`: -0.17 [-0.17], -0.70 [-0.73], -1.07 [-1.07], -1.01 [-1.01], -0.93 [-1.01], 0.03 [-0.09]
- `fb-claude-opus-5-5_walker2d_H2_01`: -0.07 [-0.07], -1.05 [-1.04], -0.99 [-0.99], -1.10 [-1.03], 0.54 [0.53], 0.77 [0.78]
- `fb-claude-opus-5-5_walker2d_H2_02`: -0.68 [-0.68], -0.96 [-0.96], -1.07 [-1.07], -2.06 [-2.09], -2.93 [-2.75], -2.02 [-1.91]
- `fb-claude-opus-5-5_walker2d_H2_03`: -1.02 [-1.02], -0.07 [-0.07], -0.43 [-0.42], -1.07 [-1.06], -1.07 [-1.07], 0.06 [0.06]
- `fb-claude-opus-5-5_walker2d_H2_04`: -0.40 [-0.36], -1.03 [-1.04], -0.07 [-0.07], -1.12 [-1.13], -1.15 [-1.13], -0.97 [-0.97]
- `fb-claude-opus-5-5_walker2d_H2_05`: -1.17 [-1.15], -0.83 [-0.83], -1.38 [-1.33], -1.13 [-1.09], -1.78 [-1.84], -2.35 [-2.26]
- `fb-claude-opus-5-5_walker2d_H2_06`: -0.68 [-1.03], -1.08 [-1.09], -1.19 [-1.21], -0.07 [-0.07], -1.10 [-1.11], -1.23 [-1.23]
- `fb-claude-opus-5-5_walker2d_H2_07`: -1.02 [-1.04], -0.08 [-0.08], -1.05 [-0.77], -0.57 [-0.66], -0.95 [-0.95], -1.70 [-1.40]
- `fb-claude-opus-5-5_walker2d_H2_08`: -1.19 [-1.19], -0.70 [-0.71], -1.38 [-1.37], -0.08 [-0.08], -6.72 [-6.72], -6.57 [-6.57]
- `fb-claude-opus-5-5_walker2d_H2_09`: -0.94 [-0.92], -1.19 [-1.20], -1.03 [-1.03], -1.26 [-1.26], -1.25 [-1.25], 0.83 [0.81]
- `fb-claude-sonnet-5-5_walker2d_H2_00`: -0.03 [-0.02], -0.74 [-0.73], -0.21 [-0.21], 0.86 [0.89], 0.10 [-0.05], 0.14 [0.02]
- `fb-claude-sonnet-5-5_walker2d_H2_01`: 0.14 [0.14], -1.07 [-0.93], -0.88 [-0.84], 0.23 [0.45], 0.82 [0.83], 0.84 [0.85]
- `fb-claude-sonnet-5-5_walker2d_H2_02`: -0.22 [-0.22], 0.34 [0.33], 0.59 [0.66], -0.96 [-0.96], 0.26 [0.25], 0.59 [0.66]
- `fb-claude-sonnet-5-5_walker2d_H2_03`: -0.05 [-0.04], 0.76 [0.75], -0.96 [-0.83], 0.53 [0.53], -1.10 [-1.11], 0.76 [0.75]
- `fb-claude-sonnet-5-5_walker2d_H2_04`: 0.07 [0.07], -0.93 [-0.93], 0.95 [0.95], 0.89 [0.90], 0.91 [0.89], 0.97 [0.96]
- `fb-claude-sonnet-5-5_walker2d_H2_05`: -0.07 [-0.07], -0.94 [-0.94], 0.82 [0.78], 0.79 [0.89], 0.49 [-0.14], 0.82 [0.65]
- `fb-claude-sonnet-5-5_walker2d_H2_06`: -0.09 [-0.09], -0.02 [-0.02], -0.07 [-0.07], -0.02 [-0.02], -0.95 [-0.98], -0.90 [-0.90]
- `fb-claude-sonnet-5-5_walker2d_H2_07`: 0.04 [0.04], -0.94 [-0.94], -1.05 [-1.05], 0.85 [0.87], 0.75 [0.81], -0.95 [-0.95]
- `fb-claude-sonnet-5-5_walker2d_H2_08`: -0.07 [-0.07], -0.08 [-0.08], 0.35 [0.36], -0.92 [-0.93], 0.21 [0.21], 0.35 [0.36]
- `fb-claude-sonnet-5-5_walker2d_H2_09`: 0.13 [0.12], -1.00 [-1.00], -0.92 [-0.92], -0.61 [-0.60], 0.70 [0.61], 0.88 [0.68]

## Budget

Claude calls (rounds, incl. repeats kept as rK/): 240; transport failures repeated: 0; tokens in (incl. cache): 2858684; tokens out: 1738817.

## Verdict (prereg s6)

- hopper: **did not work** with feedback either: no arm meets the target (20 of 20 attempts complete).
- walker2d: **did not work** with feedback either: no arm meets the target (20 of 20 attempts complete).
