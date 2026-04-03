class SolArkAPIError(RuntimeError):
    def __init__(self, code: int, message: str, payload: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.payload = payload or {}
        super().__init__(f"Sol-Ark API error {code}: {message}")
