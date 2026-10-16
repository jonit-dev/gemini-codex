# PRD — Argon through gcodex

**Status:** DONE
**Priority:** P1 — Argon cannot currently be selected through the gcodex gateway.
**Complexity:** 4 (MEDIUM); security risk promotes transport implementation to HIGH if credentials change.
**Owner:** Codex
**Depends on:** None

## Context
Google lists Argon for paid AI Pro in the Antigravity app/CLI, excluding the legacy IDE. Current gateway uses IDE OAuth and User-Agent. Auth restored on 2026-10-15; Google returned 404 for gemini-4-argon and gemini-4-argon-medium. Google model discovery has no Argon. Installed agy 1.1.27 also lists no Argon.

## Solution
First update and ping the official CLI with an explicit Argon model. Investigate its supported connection only if the live ping works. Reuse gateway translation and model overlays rather than introduce a second agent harness. Preserve existing user edits, account backups, and Flash behavior. Never print credentials or claim success from a fallback model.

## Acceptance Criteria
- [x] AC-1 [local]: Official current CLI answers an explicit Argon prompt. Proof: `agy --model gemini-4-argon-high -p 'Reply with exactly: ARGON_ALIVE'`. Result: official CLI 1.4.0 on paid personal Pro returned ARGON_ALIVE.
- [x] AC-2 [local]: gcodex explicitly selects Argon and receives ARGON_ALIVE. Proof: `gcodex -m gemini-4-argon exec 'Reply with exactly: ARGON_ALIVE'` plus backend identity validation. Result: gcodex ran pwd and returned ARGON_ALIVE with medium reasoning; live backend modelVersion gemini-4-argon-trial.
- [x] AC-3 [local]: Changed integration preserves Flash and tool-call translation. Proof: affected existing tests and a bounded real tool roundtrip. Result: 164 tests passed; Flash HTTP 200/FLASH_ALIVE; Argon shell roundtrip succeeded; patch revert/reapply/idempotence checked in a temporary package copy.

## Integration Ledger
| Capability | Consumer | Disposition | Evidence |
|---|---|---|---|
| Argon selection | gcodex launcher → local gateway → Google | Existing Flash remains default | AC-2 live gcodex shell roundtrip |

## Execution Phases
### Phase 1: Official CLI availability
**Status:** DONE
**Files:** Installed official agy CLI; updated from 1.1.27 to 1.4.0.
**Implementation:** Update official CLI; discover model IDs; ping Argon.
**Verification:** Explicit Argon response without fallback (AC-1).

### Phase 2: Gateway integration
**Status:** DONE
**Files:** cli_identity.py, patch-gateway.py, setup.sh, tests/test_cli_identity.py, tests/test_hardening.py, README.md, STABILITY.md.
**Implementation:** Smallest supported transport/auth change and model registration.
**Verification:** Focused regression tests, real Argon prompt and tool roundtrip (AC-2/3).

## Decisions
- 2026-10-15: Both existing gateway OAuth and fresh CLI OAuth advertise Argon with the CLI User-Agent. No scope or credential-store change is required. The CLI identity, rather than account eligibility, caused the legacy gateway 404. A direct generation with the CLI identity returned ARGON_ALIVE and modelVersion gemini-4-argon-trial.
- Isolated lane: .worktrees/argon-cli; branch feat/argon-cli; base 01b923392d58da65955279abf031b94e6e471f4f; owner Codex; cleanup completed: checkout removed after its committed feature patch was verified in main and no process used the checkout; 644 KiB removed. Existing primary checkout edits preserved.
- 164 tests passed in isolated checkout; shell syntax and git diff checks passed.

- User requested Argon default reasoning remain medium; the canonical Argon catalog entry defaults to medium and maps to gemini-4-argon-medium. Flash remains the launcher default.

- save-tokens skill: added opt-in canonical Argon medium, low, and high routes; left the existing routine ladder unchanged. The real arm.sh --read route invoked gcodex, completed a shell-tool call, and returned ARGON_ARM_OK with exit 0. Skill files live outside this Git repository under ~/.agents/skills/save-tokens.
