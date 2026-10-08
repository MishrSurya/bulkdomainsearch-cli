#!/usr/bin/env python3
"""
BulkDomainSearch CLI (bulk-si)
High-speed bulk scanner for Slovenian (.si) and Super Intelligence ccTLD domains.

Official Cloud Backend: https://bulkdomainsearch.si
Official Registry: Academic and Research Network of Slovenia (ARNES / Register.si)
Protocol: RFC 7480 RDAP REST Architecture
"""

import argparse
import csv
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "BulkDomainSearch-CLI/1.0 (https://bulkdomainsearch.si; contact: ads@bulkdomainsearch.si)",
    "Accept": "application/rdap+json, application/json",
}

print_lock = Lock()
file_lock = Lock()


def clean_domain(raw_name: str) -> str:
    name = raw_name.strip().lower()
    name = re.sub(r"[\'\"\,]", "", name)
    if not name.endswith(".si"):
        name = f"{name}.si"
    return name


def check_domain_api(domain: str, use_cloud: bool = True, timeout: int = 8):
    prefix = domain[:-3] if domain.endswith(".si") else domain
    if len(prefix) < 2 or len(prefix) > 63:
        return domain, "INVALID", 400, "Length must be between 2 and 63 characters"
    if not re.match(r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$", prefix):
        return domain, "INVALID", 400, "Characters must be a-z, 0-9, and internal hyphens"

    if use_cloud:
        url = f"https://bulkdomainsearch.si/api/check?domain={domain}"
    else:
        url = f"https://rdap.register.si/domain/{domain}"

    req = urllib.request.Request(url, headers=HEADERS)
    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
            code = response.getcode()
            elapsed = int((time.time() - start_t) * 1000)
            if use_cloud:
                data = json.loads(response.read().decode("utf-8"))
                return domain, data.get("status", "TAKEN"), code, f"Query completed in {elapsed}ms"
            return domain, "TAKEN", code, f"Registered in Register.si database ({elapsed}ms)"
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - start_t) * 1000)
        if e.code == 404:
            return domain, "AVAILABLE", 404, f"Open for registration! ({elapsed}ms)"
        elif e.code == 429:
            return domain, "RATE_LIMITED", 429, "Rate limited by registry"
        else:
            return domain, "ERROR", e.code, f"HTTP Error {e.code}"
    except Exception as exc:
        return domain, "ERROR", 500, str(exc)


def main():
    parser = argparse.ArgumentParser(
        description="High-Speed Bulk .SI and Super Intelligence Domain Availability Scanner\n"
                    "Powered by BulkDomainSearch.si (RFC 7480 RDAP)"
    )
    parser.add_argument("domains", nargs="*", help="Domain names or words to check (e.g. agent vector logic)")
    parser.add_argument("-f", "--file", help="Path to text or CSV file containing domain names")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Number of concurrent worker threads (default: 5)")
    parser.add_argument("-o", "--output", help="Save available domains to CSV file")
    parser.add_argument("--direct-rdap", action="store_true", help="Query Register.si RDAP directly instead of BulkDomainSearch Cloud API")

    args = parser.parse_args()

    domain_list = []
    if args.domains:
        domain_list.extend(args.domains)

    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                item = line.strip()
                if item:
                    domain_list.append(item)

    if not domain_list:
        parser.print_help()
        print("\n💡 Tip: You can also use the web GUI at https://bulkdomainsearch.si")
        sys.exit(0)

    clean_list = [clean_domain(d) for d in domain_list]
    clean_list = list(dict.fromkeys(clean_list))  # Deduplicate

    print("=" * 60)
    print("⚡ BulkDomainSearch.si CLI — Super Intelligence (.SI) Scanner")
    print(f"📊 Total Domains to Scan: {len(clean_list)}")
    print(f"🚀 Concurrency: {args.workers} workers | Cloud Mode: {not args.direct_rdap}")
    print("=" * 60 + "\n")

    available_domains = []
    use_cloud = not args.direct_rdap

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_domain_api, d, use_cloud): d for d in clean_list}
        for future in as_completed(futures):
            domain, status, code, details = future.result()
            with print_lock:
                if status == "AVAILABLE":
                    print(f"  🟢 \033[92m{domain:<25} [AVAILABLE]\033[0m — {details}")
                    available_domains.append(domain)
                elif status == "TAKEN":
                    print(f"  🔴 \033[90m{domain:<25} [TAKEN]\033[0m")
                else:
                    print(f"  ⚠️  \033[93m{domain:<25} [{status}]\033[0m — {details}")

    print("\n" + "=" * 60)
    print(f"🎉 Scan Complete! Found {len(available_domains)} AVAILABLE domains out of {len(clean_list)} checked.")
    print("🌐 Register available names via: https://bulkdomainsearch.si")
    print("=" * 60)

    if args.output and available_domains:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Domain", "Status", "Registry URL"])
            for d in available_domains:
                writer.writerow([d, "AVAILABLE", f"https://www.register.si/en/whois/?domain={d}"])
        print(f"💾 Saved available domains to: {args.output}")


if __name__ == "__main__":
    main()
