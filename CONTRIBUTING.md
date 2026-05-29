# Contributing to webex-byova

Thank you for contributing to the Webex BYOVA Python SDK.

## Development setup

```bash
git clone <your-fork>
cd BYOVA_SDK_STARTER
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v
ruff check src tests
ruff format src tests
```

## Pull request process

1. Fork the repository and create a feature branch.
2. Add tests for new behavior.
3. Ensure `pytest` and `ruff check` pass.
4. Update documentation under `docs/` for user-facing changes.
5. Open a pull request with a clear description and test plan.

## Release process (maintainers)

1. Update version in `pyproject.toml` and `src/webex_byova/__init__.py`.
2. Tag release: `git tag v0.x.x`
3. GitHub Actions publishes to PyPI via trusted publishing on tag push.

## Code style

- Python 3.10+
- Type hints encouraged
- Keep public API documented with docstrings
- Match existing patterns in `src/webex_byova/`
