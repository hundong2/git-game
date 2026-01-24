---
name: python-security-uv
description: "Python development & security guidance when working inside UV environments; enforce .env-based handling for passwords/auth keys and follow UV runtime rules."
---

# Python Security & UV Rules

## Development guidelines
- Default to uv-native tooling for script entry points: run and test code through `uv run <module>` so dependency resolution, environment activation, and logging are consistent.
- Keep package versions pinned in `pyproject.toml` or `requirements.txt`; use `uv lock` (if available) or `pip-compile` before publishing to keep reproducible builds.
- Rely on uv tasks (e.g., `uv lint`, `uv test`, `uv docs`) to encapsulate linters, type checkers, and formatters so reviewers know how to reproduce each step.

## Secrets and credentials
- Place every password, API key, database URI, or certificate path inside `.env` files scoped per environment (e.g., `.env.development`, `.env.uv`) and never commit them.
- Use `python-dotenv` or uv’s built-in loader to read `.env` before other config layers; treat values as strings, then parse/validate them into typed settings objects.
- Define a `config/env_loader.py` helper that raises on missing required keys and logs ambiguous values; that helper should wrap `os.getenv`/`dotenv.get_key` and document each critical key (e.g., `SERVICE_SECRET`, `DB_PRIVATE_KEY`).
- Confirm secrets rely on secure storage (Vault/Secret Manager) for CI/CD; when running `uv` tasks locally, source `.env` via `uv env load` or `source .env` before invoking the command.
- Regularly run `uv secrets audit` (or a custom script) to ensure env files don’t leak sensitive info and to verify each credential is rotated per policy.

## Authentication & keys
- Keep authentication flows declarative: a single module (e.g., `security/auth.py`) should fetch tokens from `.env`, validate them, and expose helper functions rather than scattering credential logic.
- Enforce MFA-enabled service accounts whenever possible; document key rotation timelines inside `security/README.md` and correlate them with env variable names (e.g., `MFA_TOKEN`, `SERVICE_ACCOUNT_KEY_PATH`).
- Store key files outside version control (e.g., `secrets/service-account.key`) and reference their paths through `.env` (e.g., `SERVICE_ACCOUNT_KEY_PATH=secrets/service-account.key`). Validate file existence in startup checks.

## UV runtime rules
- UV environments expect a consistent startup command; point `uv run` at `python -m uvicorn app:app` or the uv entry point so that hot reload, logging, and instrumentation behave predictably.
- Document required UV variables (e.g., `UV_ENV`, `UV_HOST`, `UV_PORT`) in `.env.uv` files and guard them with explicit defaults inside `config/settings.py` using uv-safe parsing helpers.
- When deploying or running locally, rely on `uv run migrate` before service start to keep schema/state aligned; never skip this step in scripts or CI.
- Capture UV health and security telemetry via `uv metrics` commands; ensure secrets are never printed by enabling `UV_LOG_SENSITIVE=false` before any non-dry run execution.

## Reviews & validation
- Tie uv tasks to CI workflows (e.g., `uv test`, `uv security-check`) so PRs automatically enforce linting, typing, and secret detection.
- Keep a lightweight `scripts/uv_setup.py` or similar that populates `.env.uv` from templates without exposing real credentials.
- Document the above policies in `docs/security.md` or `docs/uv.md` so team members can cross-reference naming conventions, env requirements, and uv-specific rules before merging changes.
