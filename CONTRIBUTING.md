# Contributing

## Dev setup

```bash
git clone https://github.com/embedded-pro/project-documentation
cd project-documentation
python -m pip install -e ".[dev]"
```

## Running tests

```bash
# Unit tests
python -m pytest tests/unit -v

# All tests with coverage
python -m pytest --cov --cov-report=term
```

## Linting and type-checking

```bash
python -m ruff check src tests
python -m mypy src/project_documentation
```

## Release process

Releases are automated via [release-please](https://github.com/googleapis/release-please).
Merge a PR whose commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
and release-please will open a release PR automatically.
