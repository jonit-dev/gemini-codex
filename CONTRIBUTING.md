# Contributing to gemini-codex

Thanks for helping. Keep it small and boring — shortest working diff wins.

## Prerequisites

- `agy` (Antigravity CLI), `codex` (OpenAI Codex CLI), `uv`, `python3` (3.12+)

## Setup

```sh
git clone https://github.com/jonit-dev/gemini-codex.git
cd gemini-codex
./setup.sh
codex-antigravity login   # your own Google account with AI Pro, one account only
gcodex exec "Reply with exactly: ALIVE"
```

## Tests

```sh
python3 -B -m unittest discover -s tests -v
```

Add or update a test with any behavior change in `patch-gateway.py`,
`gateway_safety.py`, `cli_identity.py`, `model-catalog.py`, `skills-policy.py`,
or `cli-compat.py`.
One runnable check per fix — no frameworks beyond stdlib `unittest`.

## Pull requests

1. Fork, branch from `main` (`fix/<topic>`, `feat/<topic>`).
2. Keep the `gcodex` launcher/profile names as-is — only the repo is `gemini-codex`.
3. Never commit credentials: no `antigravity-credentials.json`,
   `antigravity-accounts.json`, `*.pem`, `*.key`, `.env`, logs, or dumps.
   `setup.sh` extracts the OAuth client from each user's own `agy` binary.
4. Run the test suite before opening the PR. Note the `uv tool upgrade
   codex-antigravity-auth` caveat in the README — re-run `patch-gateway.py --check`.
5. Describe what changed and how you verified it. Link any related issue.

## Conduct and security

- Be kind — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- Found a vulnerability? Do **not** open a public issue — see [SECURITY.md](SECURITY.md).
