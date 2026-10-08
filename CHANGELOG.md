# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-08

### Added
- **Core RDAP Engine:** High-performance asynchronous scanner for `.si` ccTLD via RFC 7480 protocols.
- **Dual Query Modes:** Support for High-Speed Cloud API or Direct ARNES registry querying (`--direct-rdap`).
- **CLI Utilities:** Console entrypoints `bulkdomainsearch` and `bulk-si`.
- **Stream Processing:** Unix pipeline integration (`cat words.txt | bulk-si`).
- **Data Export:** Structured CSV output and JSON streaming mode (`--json`).
- **Telemetry Card:** Live query-per-second (QPS) and latency benchmarking.
- **Python SDK:** Programmatic access via `from bulkdomainsearch import BulkDomainScanner`.
- **Test Suite:** Unit tests for label validation, normalization, and HTTP response handling.
- **CI Automation:** GitHub Actions matrix test workflow covering Python 3.9 through 3.12.
