#!/usr/bin/env python3
"""
BulkDomainSearch CLI launcher shim.
"""

import sys
from bulkdomainsearch.cli import main

if __name__ == "__main__":
    sys.exit(main())
