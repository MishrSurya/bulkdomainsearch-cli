"""
Core High-Performance RDAP Scanning Engine for .SI ccTLD.
RFC 7480 / RFC 9083 Compliant Architecture.
"""

import json
import random
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, Iterator, List, Optional, Tuple

from .constants import (
    DEFAULT_CLOUD_API,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_WORKERS,
    DIRECT_RDAP_BASE,
    MAX_LABEL_LENGTH,
    MIN_LABEL_LENGTH,
    TLD_SUFFIX,
    USER_AGENT,
)
from .models import DomainResult, DomainStatus, ScanSummary


def normalize_domain(raw_name: str) -> str:
    """Sanitize and normalize raw domain input to canonical .si format."""
    name = raw_name.strip().lower()
    name = re.sub(r"[\'\"\,\s]", "", name)
    if not name.endswith(TLD_SUFFIX):
        name = f"{name}{TLD_SUFFIX}"
    return name


def validate_label(label: str) -> Tuple[bool, Optional[str]]:
    """Validate domain label against official ARNES ccTLD registry specifications."""
    if len(label) < MIN_LABEL_LENGTH:
        return False, f"Length must be at least {MIN_LABEL_LENGTH} characters"
    if len(label) > MAX_LABEL_LENGTH:
        return False, f"Length cannot exceed {MAX_LABEL_LENGTH} characters"
    if not re.match(r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$", label):
        return False, "Characters must be alphanumeric (a-z, 0-9) with no leading/trailing hyphen"
    return True, None


class BulkDomainScanner:
    """
    Concurrent RFC 7480 RDAP Domain Scanner.
    Supports dual modes: High-Speed Cloud API or Direct Registry Protocol.
    """

    def __init__(
        self,
        workers: int = DEFAULT_WORKERS,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
        use_direct_rdap: bool = False,
    ):
        self.workers = max(1, workers)
        self.timeout = max(1, timeout)
        self.max_retries = max(0, max_retries)
        self.use_direct_rdap = use_direct_rdap

        # Resilient SSL Context for ARNES intermediate certificate chain
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/rdap+json, application/json",
        }

    def check_domain(self, domain_name: str) -> DomainResult:
        """Query availability for a single domain name with exponential backoff retry."""
        canonical_domain = normalize_domain(domain_name)
        label = canonical_domain[:-len(TLD_SUFFIX)]
        length = len(label)

        # 1. Syntactic Pre-Validation
        is_valid, validation_err = validate_label(label)
        if not is_valid:
            return DomainResult(
                domain=canonical_domain,
                status=DomainStatus.INVALID,
                http_code=400,
                details=validation_err or "Invalid label structure",
                elapsed_ms=0,
                length=length,
                error=validation_err,
            )

        # 2. Endpoint Selection
        if self.use_direct_rdap:
            target_url = f"{DIRECT_RDAP_BASE}/{canonical_domain}"
        else:
            target_url = f"{DEFAULT_CLOUD_API}?domain={canonical_domain}"

        # 3. Network Request with Retries & Jitter
        retries = 0
        backoff_sec = 0.5

        while True:
            start_time = time.perf_counter()
            req = urllib.request.Request(target_url, headers=self._headers)

            try:
                with urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_context) as resp:
                    elapsed = int((time.perf_counter() - start_time) * 1000)
                    status_code = resp.getcode()

                    if not self.use_direct_rdap:
                        payload = json.loads(resp.read().decode("utf-8"))
                        status_str = payload.get("status", DomainStatus.TAKEN.value)
                        return DomainResult(
                            domain=canonical_domain,
                            status=DomainStatus(status_str),
                            http_code=status_code,
                            details=payload.get("details", f"Checked via cloud API ({elapsed}ms)"),
                            elapsed_ms=elapsed,
                            length=length,
                        )

                    # Direct RDAP HTTP 200 = Active / Taken
                    return DomainResult(
                        domain=canonical_domain,
                        status=DomainStatus.TAKEN,
                        http_code=status_code,
                        details=f"Registered in ARNES registry ({elapsed}ms)",
                        elapsed_ms=elapsed,
                        length=length,
                    )

            except urllib.error.HTTPError as http_err:
                elapsed = int((time.perf_counter() - start_time) * 1000)
                # RFC 7480: HTTP 404 designates unregistered domain
                if http_err.code == 404:
                    return DomainResult(
                        domain=canonical_domain,
                        status=DomainStatus.AVAILABLE,
                        http_code=404,
                        details=f"Available for registration ({elapsed}ms)",
                        elapsed_ms=elapsed,
                        length=length,
                    )
                elif http_err.code == 429:
                    retries += 1
                    if retries <= self.max_retries:
                        sleep_duration = backoff_sec + random.uniform(0.1, 0.4)
                        time.sleep(sleep_duration)
                        backoff_sec *= 2
                        continue
                    return DomainResult(
                        domain=canonical_domain,
                        status=DomainStatus.RATE_LIMITED,
                        http_code=429,
                        details="Rate limit exceeded by registry after retries",
                        elapsed_ms=elapsed,
                        length=length,
                        error="HTTP 429",
                    )
                else:
                    return DomainResult(
                        domain=canonical_domain,
                        status=DomainStatus.ERROR,
                        http_code=http_err.code,
                        details=f"Registry HTTP error {http_err.code}",
                        elapsed_ms=elapsed,
                        length=length,
                        error=str(http_err),
                    )

            except Exception as exc:
                elapsed = int((time.perf_counter() - start_time) * 1000)
                retries += 1
                if retries <= self.max_retries:
                    time.sleep(0.3)
                    continue
                return DomainResult(
                    domain=canonical_domain,
                    status=DomainStatus.ERROR,
                    http_code=500,
                    details=f"Network query error: {exc}",
                    elapsed_ms=elapsed,
                    length=length,
                    error=str(exc),
                )

    def scan_stream(
        self,
        domain_names: Iterable[str],
        callback: Optional[Callable[[DomainResult], None]] = None,
    ) -> Iterator[DomainResult]:
        """Asynchronously scan a collection of domain names yielding results as they resolve."""
        clean_list = list(dict.fromkeys(normalize_domain(d) for d in domain_names if d.strip()))

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.check_domain, d): d for d in clean_list}
            for future in as_completed(futures):
                res = future.result()
                if callback:
                    callback(res)
                yield res

    def scan_batch(
        self,
        domain_names: Iterable[str],
        callback: Optional[Callable[[DomainResult], None]] = None,
    ) -> Tuple[List[DomainResult], ScanSummary]:
        """Execute a batch scan and return complete results accompanied by timing telemetry."""
        start_time = time.perf_counter()
        results: List[DomainResult] = []

        for item in self.scan_stream(domain_names, callback=callback):
            results.append(item)

        total_duration = time.perf_counter() - start_time
        summary = ScanSummary(
            total=len(results),
            available_count=sum(1 for r in results if r.is_available),
            taken_count=sum(1 for r in results if r.status == DomainStatus.TAKEN),
            invalid_count=sum(1 for r in results if r.status == DomainStatus.INVALID),
            error_count=sum(1 for r in results if r.status in (DomainStatus.ERROR, DomainStatus.RATE_LIMITED)),
            total_time_seconds=total_duration,
        )

        return results, summary
