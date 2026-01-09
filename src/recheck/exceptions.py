"""Custom exceptions for recheck."""


class RecheckError(Exception):
    """Base exception for all recheck errors."""

    pass


class ParseError(RecheckError):
    """Raised when a regex pattern cannot be parsed."""

    def __init__(self, message: str, position: int = -1) -> None:
        self.position = position
        super().__init__(message)

    def __str__(self) -> str:
        if self.position >= 0:
            return f"{super().__str__()} at position {self.position}"
        return super().__str__()


class TimeoutError(RecheckError):
    """Raised when analysis times out."""

    pass


class CancelledException(RecheckError):
    """Raised when analysis is cancelled."""

    pass


class InvalidRegexError(RecheckError):
    """Raised when the regex is invalid."""

    pass
