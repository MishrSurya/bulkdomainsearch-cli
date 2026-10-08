"""
Domain-specific exceptions for BulkDomainSearch scanner.
"""

class BulkDomainSearchError(Exception):
    """Base exception for all BulkDomainSearch errors."""
    pass


class InvalidDomainError(BulkDomainSearchError):
    """Raised when domain name violates registry validation rules."""
    def __init__(self, domain: str, reason: str):
        super().__init__(f"Invalid domain '{domain}': {reason}")
        self.domain = domain
        self.reason = reason


class RDAPProtocolError(BulkDomainSearchError):
    """Raised when registry RDAP server returns an unhandled protocol code."""
    def __init__(self, domain: str, status_code: int, message: str):
        super().__init__(f"RDAP error for '{domain}' [HTTP {status_code}]: {message}")
        self.domain = domain
        self.status_code = status_code
        self.message = message


class RateLimitError(RDAPProtocolError):
    """Raised when registry signals HTTP 429 Too Many Requests."""
    def __init__(self, domain: str):
        super().__init__(domain, 429, "Rate limit exceeded by registry authority")
