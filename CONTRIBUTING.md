# Contributing to bulkdomainsearch-cli

Thank you for your interest in contributing to **bulkdomainsearch-cli**!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MishrSurya/bulkdomainsearch-cli.git
   cd bulkdomainsearch-cli
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

## Running Tests

Run the test suite via the standard `unittest` runner:
```bash
python -m unittest discover -s tests -v
```

## Pull Request Guidelines

- Ensure all existing tests pass and add unit tests for new functionality.
- Adhere to PEP 8 standards with clean type annotations.
- Provide clear commit messages formatted using Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
