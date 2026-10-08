"""
BulkDomainSearch Python SDK & CLI Package.
High-speed RFC 7480 RDAP Client for Slovenian (.si) and Super Intelligence ccTLD domains.
"""

from .constants import DEFAULT_HOMEPAGE, USER_AGENT
from .models import DomainResult, DomainStatus, ScanSummary
from .scanner import BulkDomainScanner, normalize_domain, validate_label

__version__ = "1.0.0"
__author__ = "BulkDomainSearch.si Research Desk"
__all__ = [
    "BulkDomainScanner",
    "DomainResult",
    "DomainStatus",
    "ScanSummary",
    "normalize_domain",
    "validate_label",
    "check_domain",
]


def check_domain(domain_name: str, use_direct_rdap: bool = False) -> DomainResult:
    """Convenience helper to check availability for a single domain name."""
    scanner = BulkDomainScanner(workers=1, use_direct_rdap=use_direct_rdap)
    return scanner.check_domain(domain_name)
