from setuptools import setup, find_packages

setup(
    name="bulkdomainsearch-cli",
    version="1.0.0",
    description="High-speed CLI tool & SDK for scanning .si and Super Intelligence domain availability via official RDAP RFC 7480",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="BulkDomainSearch.si",
    author_email="ads@bulkdomainsearch.si",
    url="https://bulkdomainsearch.si",
    packages=find_packages(),
    py_modules=["bulk_si_cli"],
    entry_points={
        "console_scripts": [
            "bulkdomainsearch=bulkdomainsearch.cli:main",
            "bulk-si=bulkdomainsearch.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
