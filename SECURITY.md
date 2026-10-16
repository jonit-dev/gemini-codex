# Security policy

## Supported versions

Latest `main` only. This is a pre-1.0 integration against upstream
`codex-antigravity-auth` and Gemini behavior — update before reporting.

## Reporting a vulnerability

Do **not** open a public issue. Use
**GitHub → Security → Report a vulnerability** (private Security Advisory).
We aim to acknowledge within 72h and triage within 7 days.

Include: affected file/commit, repro steps, expected vs actual behavior, and
whether any credential or session data is involved (do not attach any).

## Scope

In scope: auth bypass, credential leakage via this repo's scripts, path
traversal or code execution through `setup.sh` / `patch-gateway.py` /
`install-client.py`, loopback gateway exposure.

Out of scope: Google quota / `SUBSCRIPTION_REQUIRED` / ban decisions on your
account (see README **Ban risk** — unofficial OAuth path, your risk to
accept), `agy` or `codex` upstream bugs, operator misconfiguration.

## Secret handling

This repo ships **zero credentials**. Never commit `antigravity-credentials.json`,
`antigravity-accounts.json`, tokens, logs, or `/tmp` dumps. If you
accidentally push a secret, rotate it immediately and tell us via the private
channel above so we can purge history.
