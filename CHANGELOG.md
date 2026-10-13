# Changelog

## 0.2.2 - unreleased

### Fixed
- `POST /oauth/token` is never retried. Only idempotent GETs are retried, on 429/502/503/504 and connection
  errors, with exponential backoff (capped) and `Retry-After` support. New `SolArkClient` options:
  `max_retries`, `backoff_factor`, `max_backoff`, `sleep`.
- `SolArkToken` no longer shows `access_token`, `refresh_token` or `raw` in `repr()`. `SolArkClient` has a
  redacting `__repr__` and stores the password privately (the public `client.password` attribute is gone).
- `expires_in` is coerced to `int` (string values no longer crash token parsing).
- `download_plant_energy_aggregate()` raises `SolArkAPIError` when the API returns a JSON error envelope
  instead of CSV.
- Non-dict JSON payloads raise `SolArkAPIError` instead of `AttributeError`.

### Added
- `SolArkAuthError` (subclass of `SolArkAPIError`; `SolArkTokenExpiredError` now subclasses it). Raised for
  failed logins/refreshes and for auth failures reported inside HTTP 200 envelopes (heuristic: code 401/403
  or a token/login message).
- `SolArkClient.refresh()` (OAuth2 `refresh_token` grant, not verified live) and `renew()`, which tries the
  refresh token first and falls back to a password login.
- Ruff configuration; codebase formatted with `ruff format`.

## 0.2.1

- Contacts endpoint no longer available to non-installer accounts.
