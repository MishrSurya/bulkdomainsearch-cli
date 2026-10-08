"""
Command-Line Interface (CLI) implementation for BulkDomainSearch.
Engineered with production ergonomics, ANSI colorimetry, and Unix pipe support.
"""

import argparse
import csv
import json
import os
import sys
from threading import Lock
from typing import List

from .constants import (
    DEFAULT_HOMEPAGE,
    DEFAULT_TIMEOUT,
    DEFAULT_WORKERS,
    EXIT_ERROR,
    EXIT_SUCCESS,
    EXIT_USAGE,
    MAX_WORKERS,
    TerminalColor as C,
)
from .models import DomainResult, DomainStatus
from .scanner import BulkDomainScanner

# Cross-platform terminal encoding hardening
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

print_lock = Lock()


def render_banner():
    banner = f"""{C.CYAN}{C.BOLD}
  ____        _ _     ____                        _       ____  _ 
 | __ ) _   _| | | __|  _ \\  ___  _ __ ___   __ _(_)_ __ / ___|(_)
 |  _ \\| | | | | |/ /| | | |/ _ \\| '_ ` _ \\ / _` | | '_ \\\\___ \\| |
 | |_) | |_| | |   < | |_| | (_) | | | | | | (_| | | | | |___) | |
 |____/ \\__,_|_|_|\\_\\|____/ \\___/|_| |_| |_|\\__,_|_|_| |_|____/|_|
{C.RESET}{C.DIM}  RFC 7480 RDAP Client • Super Intelligence (.SI) ccTLD Registry Scanner
  Official Cloud Engine: {C.WHITE}{DEFAULT_HOMEPAGE}{C.RESET}
"""
    sys.stderr.write(banner + "\n")


def format_row(res: DomainResult) -> str:
    """Format single result row with aligned ANSI styling and encoding fallback."""
    can_unicode = True
    try:
        "\U0001f534".encode(sys.stdout.encoding or "utf-8")
    except Exception:
        can_unicode = False

    if res.status == DomainStatus.AVAILABLE:
        sym = "🟢 " if can_unicode else "[+] "
        badge = f"{C.GREEN}{C.BOLD}{sym}AVAILABLE{C.RESET}"
        timing = f"{C.DIM}[{res.elapsed_ms}ms]{C.RESET}"
        return f"  {badge}  {timing:<16} {C.WHITE}{C.BOLD}{res.domain:<24}{C.RESET} {C.GREEN}{res.details}{C.RESET}"
    elif res.status == DomainStatus.TAKEN:
        sym = "🔴 " if can_unicode else "[-] "
        badge = f"{C.RED}{sym}TAKEN    {C.RESET}"
        timing = f"{C.DIM}[{res.elapsed_ms}ms]{C.RESET}"
        return f"  {badge}  {timing:<16} {C.DIM}{res.domain:<24}{C.RESET}"
    elif res.status == DomainStatus.INVALID:
        sym = "⚠️  " if can_unicode else "[!] "
        badge = f"{C.YELLOW}{sym}INVALID  {C.RESET}"
        return f"  {badge}  {C.YELLOW}{res.domain:<24}{C.RESET} {C.DIM}({res.details}){C.RESET}"
    elif res.status == DomainStatus.RATE_LIMITED:
        sym = "⏳ " if can_unicode else "[*] "
        badge = f"{C.MAGENTA}{sym}429 LIMIT{C.RESET}"
        return f"  {badge}  {C.MAGENTA}{res.domain:<24}{C.RESET} {C.DIM}{res.details}{C.RESET}"
    else:
        sym = "❌ " if can_unicode else "[x] "
        badge = f"{C.RED}{sym}ERROR    {C.RESET}"
        return f"  {badge}  {C.RED}{res.domain:<24}{C.RESET} {C.DIM}{res.details}{C.RESET}"
        return f"  {badge}  {C.RED}{res.domain:<24}{C.RESET} {C.DIM}{res.details}{C.RESET}"


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bulkdomainsearch",
        description="High-performance RFC 7480 RDAP client for bulk scanning Slovenian (.si) and Super Intelligence domains at scale.",
        epilog=f"Web application & portfolio benchmarks: {DEFAULT_HOMEPAGE}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "domains",
        nargs="*",
        help="One or more domain names or dictionary roots to scan (e.g. agent vector compute)",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        help="Read target domain names from a local TXT or CSV file",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Concurrent scanning worker threads (1–{MAX_WORKERS}, default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Socket network timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="CSV_PATH",
        help="Export all discovered AVAILABLE domains to a structured CSV file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON array to stdout (ideal for CI/CD and jq pipes)",
    )
    parser.add_argument(
        "--available-only",
        action="store_true",
        help="Display only available domains; suppress taken or registered names",
    )
    parser.add_argument(
        "--direct-rdap",
        action="store_true",
        help="Bypass cloud API cache and query official ARNES registry RDAP endpoints directly",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Suppress ASCII decorative header in stdout/stderr",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (RFC 7480 RDAP)",
    )

    return parser.parse_args(argv)


def main(argv: List[str] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    # 1. Harvest Input Domains
    raw_domains: List[str] = []
    if args.domains:
        raw_domains.extend(args.domains)

    if args.file:
        if not os.path.isfile(args.file):
            sys.stderr.write(f"{C.RED}Error: File not found: {args.file}{C.RESET}\n")
            return EXIT_ERROR

        try:
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line and not clean_line.startswith("#"):
                        # Handle potential CSV commas
                        parts = clean_line.split(",")
                        raw_domains.append(parts[0].strip())
        except Exception as read_err:
            sys.stderr.write(f"{C.RED}Error reading file '{args.file}': {read_err}{C.RESET}\n")
            return EXIT_ERROR

    # Check for Unix stdin pipe (e.g., cat words.txt | bulk-si)
    if not sys.stdin.isatty() and not raw_domains:
        for line in sys.stdin:
            clean_line = line.strip()
            if clean_line:
                parts = clean_line.split(",")
                raw_domains.append(parts[0].strip())

    if not raw_domains:
        if not args.no_banner and not args.json:
            render_banner()
        sys.stderr.write(f"{C.YELLOW}Notice: No domain names supplied.{C.RESET}\n")
        sys.stderr.write(f"Usage: {C.WHITE}bulk-si domain1 domain2 ...{C.RESET} or {C.WHITE}bulk-si -f wordlist.txt{C.RESET}\n")
        sys.stderr.write(f"GUI: Open {C.CYAN}{DEFAULT_HOMEPAGE}{C.RESET} in your browser.\n\n")
        return EXIT_USAGE

    # 2. Render Header (if not JSON mode)
    if not args.json and not args.no_banner:
        render_banner()
        mode_label = "Direct ARNES RDAP" if args.direct_rdap else "High-Speed Cloud API"
        sys.stderr.write(
            f"  {C.BOLD}Targets:{C.RESET} {len(raw_domains):<8} "
            f"{C.BOLD}Workers:{C.RESET} {args.workers:<6} "
            f"{C.BOLD}Engine:{C.RESET} {mode_label}\n"
        )
        sys.stderr.write(f"  {C.DIM}{'─' * 68}{C.RESET}\n\n")

    # 3. Instantiate Engine & Execute Scan
    scanner = BulkDomainScanner(
        workers=args.workers,
        timeout=args.timeout,
        use_direct_rdap=args.direct_rdap,
    )

    def live_printer(res: DomainResult):
        if args.json:
            return
        if args.available_only and not res.is_available:
            return
        with print_lock:
            sys.stdout.write(format_row(res) + "\n")
            sys.stdout.flush()

    results, summary = scanner.scan_batch(raw_domains, callback=live_printer)

    # 4. JSON Output Handling
    if args.json:
        payload = {
            "summary": {
                "total": summary.total,
                "available": summary.available_count,
                "taken": summary.taken_count,
                "invalid": summary.invalid_count,
                "errors": summary.error_count,
                "duration_seconds": round(summary.total_time_seconds, 3),
                "speed_qps": summary.speed_qps,
            },
            "results": [r.to_dict() for r in results],
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return EXIT_SUCCESS

    # 5. Summary Telemetry Box
    sys.stderr.write(f"\n  {C.DIM}{'─' * 68}{C.RESET}\n")
    sys.stderr.write(
        f"  {C.BOLD}Summary:{C.RESET} "
        f"{C.GREEN}{C.BOLD}{summary.available_count} Available{C.RESET} | "
        f"{C.RED}{summary.taken_count} Taken{C.RESET} | "
        f"{summary.total} Total in {summary.total_time_seconds:.2f}s "
        f"({C.CYAN}{summary.speed_qps} QPS{C.RESET})\n"
    )

    # 6. CSV Export
    if args.output:
        available_domains = [r for r in results if r.is_available]
        try:
            with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["domain", "status", "http_code", "length", "registry_url"])
                for r in available_domains:
                    writer.writerow([
                        r.domain,
                        r.status.value,
                        r.http_code,
                        r.length,
                        f"https://www.register.si/en/whois/?domain={r.domain}",
                    ])
            sys.stderr.write(f"  {C.GREEN}✔ Exported {len(available_domains)} available domains to: {args.output}{C.RESET}\n")
        except Exception as write_err:
            sys.stderr.write(f"  {C.RED}❌ Error saving CSV '{args.output}': {write_err}{C.RESET}\n")

    sys.stderr.write(f"  {C.DIM}Register available names instantly at: {DEFAULT_HOMEPAGE}{C.RESET}\n\n")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
