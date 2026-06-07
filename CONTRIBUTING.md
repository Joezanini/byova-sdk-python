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

## Documentation

Install docs dependencies and preview the site:

```bash
pip install -e ".[docs]"
mkdocs serve -f docs/mkdocs.yml   # http://127.0.0.1:8000
mkdocs build -f docs/mkdocs.yml --strict
```

User-facing changes should update pages under `docs/` and public API docstrings in `src/webex_byova/`.

## Pull request process

1. Fork the repository and create a feature branch.
2. Add tests for new behavior.
3. Ensure `pytest` and `ruff check` pass.
4. Update documentation under `docs/` for user-facing changes.
5. Open a pull request with a clear description and test plan.

## Release process (maintainers)

1. Merge changes to `main`.
2. Create and push a version tag (version is derived from the tag via hatch-vcs):

   ```bash
   git tag v0.x.x
   git push origin v0.x.x
   ```

3. GitHub Actions runs tests, builds the package, and publishes to PyPI via trusted publishing.

### One-time PyPI setup

- Create a GitHub environment named `pypi.org`.
- Configure [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) for this repository:
  - Workflow: `release.yml`
  - Environment: `pypi.org`
- Optionally set repository variable `PYPI_REPOSITORY_URL` to `https://test.pypi.org/legacy/` for TestPyPI dry runs.

## Code style

- Python 3.10+
- Type hints encouraged
- Keep public API documented with docstrings
- Match existing patterns in `src/webex_byova/`
