# project-documentation

[![CI](https://github.com/embedded-pro/project-documentation/actions/workflows/ci.yml/badge.svg)](https://github.com/embedded-pro/project-documentation/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/project-documentation)](https://pypi.org/project/project-documentation/)
[![Python](https://img.shields.io/pypi/pyversions/project-documentation)](https://pypi.org/project/project-documentation/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

> Documentation pipeline for embedded projects — CI-friendly, framework-agnostic.

`project-documentation` is a GitHub composite action and Python package that covers the full documentation lifecycle for embedded software projects:

- **Validate requirements** — check YAML requirement files against a JSON schema
- **Validate documents** — enforce frontmatter fields and required sections in Markdown architecture/design/theory documents
- **Generate requirements PDF** — render YAML requirements to a versioned PDF via a Markdown template
- **Build documentation PDFs** — convert Markdown documentation directories and YAML requirements to PDFs using Pandoc
- **Traceability matrix** — map requirements to Gherkin scenarios (with optional JUnit pass/fail status), output Markdown and optionally PDF

## ✨ Features

| Capability | Description |
|---|---|
| Requirements validation | JSON schema validation for YAML requirement files |
| Document validation | Frontmatter fields, required H2 sections, no code blocks in design docs |
| Requirements PDF | Template-driven PDF from YAML requirements |
| Documentation PDFs | Per-directory Markdown → PDF + combined requirements PDF |
| Traceability matrix | Requirements ↔ scenarios mapping with coverage statistics |
| PR comment | Idempotent PR comments (traceability matrix) |
| GitHub Action | Composite action with feature flags for each capability |

## 🚀 Quickstart

### 1. Install

```
pip install project-documentation
```

### 2. Use in GitHub Actions

```yaml
- uses: embedded-pro/project-documentation@v0
  with:
    run-validate-requirements: 'true'
    run-validate-documents: 'true'
    run-generate-requirements-pdf: 'true'
    run-build-documentation-pdfs: 'true'
    run-traceability-matrix: 'true'
    version: ${{ github.ref_name }}
```

See [docs/usage.md](docs/usage.md) for the full input/output reference.

### 3. Run from the command line

```bash
# Validate requirements against a JSON schema
project-documentation-validate-requirements \
    --schema documentation/tools/requirement.schema.json \
    --requirements-dir documentation/requirements

# Validate Markdown documentation
project-documentation-validate-documents \
    --documents-dir documentation \
    --doc-type architecture

# Generate requirements PDF
project-documentation-generate-requirements-pdf \
    --requirements-dir documentation/requirements \
    --template documentation/templates/requirements.md \
    --output documentation/output/requirements.pdf

# Build all documentation PDFs
project-documentation-build-pdfs \
    --version v1.2.3 \
    --output-dir docs-pdf \
    --docs-dirs documentation/architecture documentation/design documentation/theory \
    --requirements-dir documentation/requirements

# Generate traceability matrix
project-documentation-traceability-matrix \
    --requirements-dir documentation/requirements \
    --features-dir integration_tests/software_in_the_loop/features \
    --output docs-pdf/traceability-matrix.md \
    --junit-xml sil-test-report.xml
```

## 📚 Documentation

| File | Contents |
|---|---|
| [docs/usage.md](docs/usage.md) | CLI flags, action inputs/outputs, examples |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Dev setup, testing, release process |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

## ⚠️ System dependencies

The PDF-generating capabilities require:
- `pandoc` — document converter
- `pdflatex` (via `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`)

The GitHub Action installs these automatically when any PDF feature flag is enabled.

## 📄 License

Apache-2.0 — see [LICENSE](LICENSE).
