"""
Constants and protocol defaults for BulkDomainSearch CLI and RDAP Client.
"""

from typing import Final

DEFAULT_CLOUD_API: Final[str] = "https://bulkdomainsearch.si/api/check"
DIRECT_RDAP_BASE: Final[str] = "https://rdap.register.si/domain"
DEFAULT_HOMEPAGE: Final[str] = "https://bulkdomainsearch.si"

TLD_SUFFIX: Final[str] = ".si"
MIN_LABEL_LENGTH: Final[int] = 2
MAX_LABEL_LENGTH: Final[int] = 63

DEFAULT_WORKERS: Final[int] = 5
MAX_WORKERS: Final[int] = 20
DEFAULT_TIMEOUT: Final[int] = 8
DEFAULT_RETRIES: Final[int] = 3

USER_AGENT: Final[str] = (
    "BulkDomainSearch-CLI/1.0.0 (RFC 7480 RDAP Protocol Client; +https://bulkdomainsearch.si)"
)

# Standardized Exit Codes (Sysexits convention)
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1
EXIT_USAGE: Final[int] = 2
EXIT_KEYBOARD_INTERRUPT: Final[int] = 130

# ANSI Terminal Styling
class TerminalColor:
    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    GREEN: str = "\033[92m"
    RED: str = "\033[91m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    MAGENTA: str = "\033[95m"
    CYAN: str = "\033[96m"
    WHITE: str = "\033[97m"
