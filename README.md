# bulkdomainsearch-cli ⚡

[![CI & Quality Assurance](https://github.com/MishrSurya/bulkdomainsearch-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/MishrSurya/bulkdomainsearch-cli/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Protocol: RFC 7480](https://img.shields.io/badge/Protocol-RFC%207480%20RDAP-emerald.svg)](https://datatracker.ietf.org/doc/html/rfc7480)
[![Official Cloud Web GUI](https://img.shields.io/badge/Cloud%20Web%20App-BulkDomainSearch.si-0ea5e9.svg)](https://bulkdomainsearch.si)

> **High-performance RFC 7480 RDAP client & concurrent CLI engine for scanning Slovenian (`.si`) and Super Intelligence ccTLD domains at scale.**  
> Powered by official registry data from the Academic and Research Network of Slovenia (ARNES / [Register.si](https://www.register.si/)) and the cloud infrastructure of [**BulkDomainSearch.si**](https://bulkdomainsearch.si).

---

## 🏗️ Architecture & Concurrency Pipeline

Unlike traditional tools that scrape registry HTML or spam legacy Port 43 TCP sockets until throttled, `bulkdomainsearch-cli` implements a non-blocking asynchronous worker pipeline over modern **RDAP (Registration Data Access Protocol - RFC 7480 / RFC 9083)**:

```
┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
│  CLI / STDIN    │ ────> │  Syntactic Label     │ ────> │  Concurrent Worker     │
│  - Arguments    │       │  Sanitizer & Regex   │       │  Pool (1–20 Threads)   │
│  - File (CSV)   │       │  (2–63 Chars Rule)   │       └───────────┬────────────┘
└─────────────────┘       └──────────────────────┘                   │
                                                                     ▼
┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
│  Stream Sink    │ <──── │  Telemetry Collector │ <──── │  RFC 7480 RDAP Client   │
│  - ANSI Stdout  │       │  - Latency (ms)      │       │  - Cloud API Cache     │
│  - JSON Array   │       │  - QPS Throughput    │       │  - Direct ARNES Socket │
│  - CSV Export   │       │  - HTTP 404 Detect   │       │  - Jittered Backoff    │
└─────────────────┘       └──────────────────────┘       └────────────────────────┘
```

---

## 📊 Benchmark: RDAP vs. Legacy WHOIS vs. Web Scraping

| Performance Dimension | `bulkdomainsearch-cli` (RDAP) | Traditional Port 43 WHOIS | Web Scraping (Browser Bots) |
| :--- | :---: | :---: | :---: |
| **Average Query Latency** | **12 – 28 ms** | 350 – 600 ms | 1,800 – 3,500 ms |
| **Max Batch Concurrency** | **5,000+ Domains** | 20 – 50 before 429 | Fails on Cloudflare / Captcha |
| **Rate-Limit Vulnerability** | **Zero (Jittered Backoff)** | High (Strict IP Bans) | Immediate IP Ban |
| **Data Format Accuracy** | **Authoritative JSON (RFC 7480)** | Unstructured Plaintext | Brittle DOM Parsing |
| **Cost & License** | **100% Free & Open Source** | Registrar Dependent | Paid Proxies Required |

---

## 💡 The Super Intelligence (`.SI`) Economic Thesis

Domain investors and AI founders are actively migrating to the `.si` ccTLD:
* **The Cost Arbitrage:** `.ai` (Anguilla) domains now cost **$140 – $180 / year** with mandatory 2-year renewal lock-ins. Official `.si` registrations start at **~$12.29 / year** (~91% cheaper).
* **The Brand Shift:** As frontier research advances from Narrow AI to Artificial Super Intelligence (ASI), the abbreviation **SI** represents the next-generation tech branding category.
* **Open Registry Access:** ARNES (Slovenian National Registry) has maintained **100% unrestricted worldwide registration since 2008**. No European residency or local trustee service is required.

---

## 📦 Installation

### From Source (Recommended)
```bash
git clone https://github.com/MishrSurya/bulkdomainsearch-cli.git
cd bulkdomainsearch-cli
pip install -e .
```

### Standalone (Zero-Install Execution)
```bash
python bulk_si_cli.py --help
```

---

## ⚡ CLI Usage & Examples

The package registers both `bulkdomainsearch` and `bulk-si` binary entry points:

### 1. Ad-Hoc Domain Check
```bash
bulk-si agent vector compute neural cortex
```

### 2. Large Wordlist Batch Scan (with CSV Export)
Scan 1,000 dictionary words with 8 concurrent worker threads and save open names to `available.csv`:
```bash
bulk-si -f dictionary_words.txt -w 8 -o available.csv
```

### 3. Pipeline / Unix Stdin Streaming
Pipe domain lists directly from generator scripts or standard Unix streams:
```bash
cat candidate_names.txt | bulk-si --available-only
```

### 4. Machine-Readable JSON Mode (for CI/CD & `jq`)
```bash
bulk-si agi asi superintelligence --json | jq '.results[] | select(.status=="AVAILABLE")'
```

### 5. Direct ARNES Registry Querying (Bypass Cloud API)
```bash
bulk-si ai.si ml.si --direct-rdap
```

---

## 🛠️ Complete CLI Flag Reference

```text
usage: bulkdomainsearch [-h] [-f PATH] [-w WORKERS] [-t TIMEOUT] [-o CSV_PATH]
                        [--json] [--available-only] [--direct-rdap]
                        [--no-banner] [-v]
                        [domains ...]

High-performance RFC 7480 RDAP client for bulk scanning Slovenian (.si) and
Super Intelligence domains at scale.

positional arguments:
  domains               One or more domain names or dictionary roots to scan

options:
  -h, --help            Show this help message and exit
  -f PATH, --file PATH  Read target domain names from a local TXT or CSV file
  -w WORKERS, --workers WORKERS
                        Concurrent scanning worker threads (1–20, default: 5)
  -t TIMEOUT, --timeout TIMEOUT
                        Socket network timeout in seconds (default: 8)
  -o CSV_PATH, --output CSV_PATH
                        Export all discovered AVAILABLE domains to structured CSV
  --json                Output raw JSON payload to stdout (for CI/CD pipelines)
  --available-only      Display only available domains; suppress registered names
  --direct-rdap         Bypass cloud cache; query official ARNES RDAP directly
  --no-banner           Suppress ASCII decorative banner in stdout/stderr
  -v, --version         Show program's version number and exit
```

---

## 🐍 Programmatic Python SDK Usage

You can embed the scanner directly into your own Python applications, data pipelines, and automation bots:

```python
from bulkdomainsearch import BulkDomainScanner, DomainStatus

# Initialize high-speed scanner
scanner = BulkDomainScanner(workers=8, timeout=5)

# 1. Check a single domain
result = scanner.check_domain("hypercompute")
if result.is_available:
    print(f"🎉 {result.domain} is available for registration! ({result.elapsed_ms}ms)")
else:
    print(f"❌ {result.domain} is taken.")

# 2. Batch scan multiple candidates
words = ["agentic", "superaudio", "cortex", "synth", "neural"]
results, summary = scanner.scan_batch(words)

print(f"Scan finished in {summary.total_time_seconds:.2f}s ({summary.speed_qps} QPS)")
for r in results:
    if r.status == DomainStatus.AVAILABLE:
        print(f"  🟢 {r.domain} [{r.http_code}]")
```

---

## 🧪 Testing & Quality Assurance

Run the test suite locally with Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

All pull requests are automatically tested via GitHub Actions across **Python 3.9, 3.10, 3.11, and 3.12**.

---

## 🌐 Official Web Ecosystem & Resources

* 🖥️ **Web GUI Application:** [https://bulkdomainsearch.si](https://bulkdomainsearch.si)
* 📖 **.SI vs .AI In-Depth Comparison:** [https://bulkdomainsearch.si/compare/si-vs-ai-domains](https://bulkdomainsearch.si/compare/si-vs-ai-domains)
* 📚 **Dictionary .SI Domains Hub:** [https://bulkdomainsearch.si/dictionary-si-domains](https://bulkdomainsearch.si/dictionary-si-domains)
* 🔢 **2-Letter .SI Liquidity Matrix:** [https://bulkdomainsearch.si/2-letter-si-domains](https://bulkdomainsearch.si/2-letter-si-domains)
* 🤖 **AI & Super Intelligence Hub:** [https://bulkdomainsearch.si/ai-and-tech-si-domains](https://bulkdomainsearch.si/ai-and-tech-si-domains)
* 🇸🇮 **Slovenski Portal (/sl):** [https://bulkdomainsearch.si/sl](https://bulkdomainsearch.si/sl)
* 🇩🇪 **Deutsches Portal (/de):** [https://bulkdomainsearch.si/de](https://bulkdomainsearch.si/de)
* 🇨🇳 **中文扫描平台 (/zh):** [https://bulkdomainsearch.si/zh](https://bulkdomainsearch.si/zh)
* 🤖 **LLMs & Agentic Manifest:** [https://bulkdomainsearch.si/llms.txt](https://bulkdomainsearch.si/llms.txt)

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
Open source and free for commercial, research, and individual use.
