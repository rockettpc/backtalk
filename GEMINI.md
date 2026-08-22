# backtalk: setup

You are reading the boot file of the backtalk repo. Your job in this folder is to help the user set up and test backtalk (the voice loop for Google Antigravity CLI).

When the user asks to configure or set up backtalk (e.g. "set me up" or "read backtalk.md"):
1. Read `backtalk.md` in this folder and follow it step by step.
2. Configure `backtalk.json` with their chosen settings (`agent_dir`, `name`, `ptt_key`, `voice`, `dangerously_skip_permissions`, `permission_mode`, etc.).
3. Verify dependencies and test-fire the voice loop using `./run.sh` (or `uv run python -m backtalk.main`).
