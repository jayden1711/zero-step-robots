# Third-party code, models and tools

Nothing listed here is committed or redistributed. Add a row **before** first use: upstream, pinned
version/commit, license. Apache/BSD/MIT only unless the owner approves otherwise.

| Item | Upstream | Version | License | Use |
|---|---|---|---|---|
| Gymnasium | github.com/Farama-Foundation/Gymnasium | 1.4.0 (PyPI) | MIT | cartpole, hopper envs |
| MuJoCo | github.com/google-deepmind/mujoco | 3.17.0 (PyPI) | Apache-2.0 | physics |
| Stable-Baselines3 (PPO), with PyTorch (BSD-3) | github.com/DLR-RM/stable-baselines3 | 2.9.2 / torch 2.15.0 cpu (PyPI) | MIT | PPO control |
| llama.cpp (local model server, built in ~/opt/wiif) | github.com/ggml-org/llama.cpp | commit 69ee2ecc0 | MIT | serves local models |
| Qwen3-Coder-30B-A3B-Instruct (Q4_K_M GGUF, in ~/models) | Qwen team, via a GGUF conversion [verify exact source] | SHA-256 in ~/models/SHA256SUMS.wiif | Apache-2.0 [verify] | local LLM arm |
| gpt-oss-20b (MXFP4 GGUF, in ~/models) | OpenAI | SHA-256 in ~/models/SHA256SUMS.wiif | Apache-2.0 [verify] | local LLM arm |
| Claude Code CLI (`claude -p`) | Anthropic | 2.1.282 (recorded per attempt) | commercial terms (subscription) | hosted LLM arm; not redistributed |
| Walking policy for Part B | humanoid-on-a-chip's distilled walker (upstream sources in that repo's THIRD_PARTY.md) | | per source | Part B |

LLMs used for attempts are recorded per attempt in results/ (model, version, interface: subscription UI or local).
