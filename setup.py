from setuptools import setup, find_packages

setup(
    name="bulkdomainsearch-cli",
    version="1.0.0",
    description="High-speed CLI tool for scanning .si and Super Intelligence domain availability via official RDAP RFC 7480",
    author="BulkDomainSearch.si",
    author_email="ads@bulkdomainsearch.si",
    url="https://bulkdomainsearch.si",
    py_modules=["bulk_si_cli"],
    entry_points={
        "console_scripts": [
            "bulkdomainsearch=bulk_si_cli:main",
            "bulk-si=bulk_si_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
