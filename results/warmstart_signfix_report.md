# Sign-repair report (addendum docs/addendum-2026-11-16-signfix.md)

Designs: hopper L starts with pitch-to-hip net gain >= 0. S = obs[1] gain flipped on every unit feeding a0. Paired with the original run of the same design under the same optimiser. Pass = by checkpoint 500.

## CEM (primary)

n = 30 of 30 (not repairable: 1). S passes 10, original passes 2; discordant: only S 9, only original 1; one-sided exact McNemar p = 0.0107 -> **the sign is causal for search success**

- `cpg-claude-opus-5-5_hopper_H0_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=0.04 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_03`: S T=200 (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_07`: S T=100 (repairable True), original T=200, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_08`: S T=100 (repairable True), original T=None, repaired design with no search d=0.26 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_09`: S T=100 (repairable True), original T=None, repaired design with no search d=0.28 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_00`: S T=200 (repairable True), original T=None, repaired design with no search d=0.23 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_02`: S T=100 (repairable True), original T=None, repaired design with no search d=-0.11 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_03`: S T=None (repairable True), original T=None, repaired design with no search d=-0.04 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_07`: S T=None (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_09`: S T=500 (repairable True), original T=None, repaired design with no search d=0.13 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=-0.07 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_01`: S T=200 (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_07`: S T=None (repairable True), original T=200, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=0.17 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_04`: S T=None (repairable False), original T=None, repaired design with no search d=-0.12 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_06`: S T=None (repairable True), original T=None, repaired design with no search d=-0.05 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_07`: S T=None (repairable True), original T=None, repaired design with no search d=-0.08 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_08`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=0.02 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=0.03 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=0.21 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_04`: S T=None (repairable True), original T=None, repaired design with no search d=0.1 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_05`: S T=None (repairable True), original T=None, repaired design with no search d=0.04 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_06`: S T=None (repairable True), original T=None, repaired design with no search d=-0.01 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_07`: S T=500 (repairable True), original T=None, repaired design with no search d=-0.01 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_08`: S T=None (repairable True), original T=None, repaired design with no search d=0.05 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_09`: S T=100 (repairable True), original T=None, repaired design with no search d=0.04 m

## HC (secondary)

n = 30 of 30 (not repairable: 1). S passes 14, original passes 4; discordant: only S 12, only original 2; one-sided exact McNemar p = 0.0065 -> **the sign is causal for search success**

- `cpg-claude-opus-5-5_hopper_H0_cpgspec_02`: S T=200 (repairable True), original T=None, repaired design with no search d=0.04 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_03`: S T=500 (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_07`: S T=100 (repairable True), original T=100, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_08`: S T=None (repairable True), original T=None, repaired design with no search d=0.26 m
- `cpg-claude-opus-5-5_hopper_H0_cpgspec_09`: S T=200 (repairable True), original T=None, repaired design with no search d=0.28 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=0.23 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=-0.11 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_03`: S T=500 (repairable True), original T=None, repaired design with no search d=-0.04 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_07`: S T=200 (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-opus-5-5_hopper_H1_cpgspec_09`: S T=None (repairable True), original T=None, repaired design with no search d=0.13 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=-0.07 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-opus-5-5_hopper_H2_cpgspec_07`: S T=500 (repairable True), original T=200, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_00`: S T=25 (repairable True), original T=None, repaired design with no search d=0.17 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_01`: S T=None (repairable True), original T=None, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=-0.03 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_04`: S T=None (repairable False), original T=None, repaired design with no search d=-0.12 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_06`: S T=None (repairable True), original T=200, repaired design with no search d=-0.05 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_07`: S T=None (repairable True), original T=None, repaired design with no search d=-0.08 m
- `cpg-claude-sonnet-5-5_hopper_H0_cpgspec_08`: S T=None (repairable True), original T=500, repaired design with no search d=-0.02 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_00`: S T=None (repairable True), original T=None, repaired design with no search d=0.02 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_01`: S T=25 (repairable True), original T=None, repaired design with no search d=0.03 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_02`: S T=None (repairable True), original T=None, repaired design with no search d=0.21 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_04`: S T=200 (repairable True), original T=None, repaired design with no search d=0.1 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_05`: S T=500 (repairable True), original T=None, repaired design with no search d=0.04 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_06`: S T=50 (repairable True), original T=None, repaired design with no search d=-0.01 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_07`: S T=500 (repairable True), original T=None, repaired design with no search d=-0.01 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_08`: S T=None (repairable True), original T=None, repaired design with no search d=0.05 m
- `cpg-claude-sonnet-5-5_hopper_H1_cpgspec_09`: S T=500 (repairable True), original T=None, repaired design with no search d=0.04 m

