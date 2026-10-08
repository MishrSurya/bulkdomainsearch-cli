# bulkdomainsearch-cli ⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Protocol: RFC 7480](https://img.shields.io/badge/Protocol-RFC_7480_RDAP-green.svg)](https://datatracker.ietf.org/doc/html/rfc7480)
[![Official Web GUI](https://img.shields.io/badge/Web_GUI-BulkDomainSearch.si-emerald)](https://bulkdomainsearch.si)

> **High-speed, multi-threaded CLI scanner for Slovenian (`.si`) and Super Intelligence ccTLD domain availability.**  
> Powered by the official cloud engine at [**BulkDomainSearch.si**](https://bulkdomainsearch.si).

---

## 🚀 Why Use This Tool?

* **Zero Rate Limits:** Queries directly via RFC 7480 RDAP REST socket endpoints, completely bypassing slow web WHOIS and captcha obstacles.
* **Bulk Scanning:** Check 500 to 5,000+ domain names in minutes using configurable asynchronous thread pools.
* **The Super Intelligence (`.si`) Movement:** Domain investors and tech founders are acquiring `.si` domains for **~$12.29/year** as a high-leverage alternative to paying $140+/year for `.ai`.
* **Instant CSV Export:** Filter open names and export ready-to-register CSV lists with one flag.

---

## 📦 Installation

### From Source
```bash
git clone https://github.com/MishrSurya/bulkdomainsearch-cli.git
cd bulkdomainsearch-cli
pip install -e .
```

Or run standalone without installing:
```bash
python bulk_si_cli.py --help
```

---

## ⚡ Quickstart & Examples

### 1. Check Multiple Domains on the Fly
```bash
bulk-si agent vector neural compute logic
```

### 2. Scan a Large Wordlist File (CSV or TXT)
```bash
bulk-si -f wordlist.txt -w 8 -o available.csv
```

### 3. Query Directly Against Register.si Registry
```bash
bulk-si agi.si asi.si --direct-rdap
```

---

## 🌐 Official Web Application & Resources

Prefer a graphical interface with drag-and-drop file upload and live charts? Use the web app:

* 🖥️ **Web Scanner GUI:** [https://bulkdomainsearch.si](https://bulkdomainsearch.si)
* 📖 **.SI vs .AI Comparison Guide:** [https://bulkdomainsearch.si/compare/si-vs-ai-domains](https://bulkdomainsearch.si/compare/si-vs-ai-domains)
* 📚 **Dictionary .SI Domains:** [https://bulkdomainsearch.si/dictionary-si-domains](https://bulkdomainsearch.si/dictionary-si-domains)
* 🔢 **2-Letter .SI Combinations:** [https://bulkdomainsearch.si/2-letter-si-domains](https://bulkdomainsearch.si/2-letter-si-domains)
* 🤖 **AI & Tech Domains Hub:** [https://bulkdomainsearch.si/ai-and-tech-si-domains](https://bulkdomainsearch.si/ai-and-tech-si-domains)
* 🇸🇮 **Slovenian Portal (/sl):** [https://bulkdomainsearch.si/sl](https://bulkdomainsearch.si/sl)
* 🇩🇪 **German Portal (/de):** [https://bulkdomainsearch.si/de](https://bulkdomainsearch.si/de)
* 🇨🇳 **Chinese Portal (/zh):** [https://bulkdomainsearch.si/zh](https://bulkdomainsearch.si/zh)

---

## 📜 License
MIT License. Open source and free for commercial and personal use.
