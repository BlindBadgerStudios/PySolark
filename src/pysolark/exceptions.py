from __future__ import annotations


class SolArkAPIError(RuntimeError):
    def __init__(self, code: int, message: str, payload: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.payload = payload or {}
        super().__init__(f"Sol-Ark API error {code}: {message}")


class SolArkAuthError(SolArkAPIError):
    """Authentication failed or the token is no longer valid.

    Raised for failed logins/refreshes and for auth failures that Sol-Ark reports inside an
    HTTP 200 JSON envelope (non-zero ``code``).
    """


class SolArkTokenExpiredError(SolArkAuthError):
    def __init__(self) -> None:
        super().__init__(401, "Access token has expired. Call login() to re-authenticate.")
