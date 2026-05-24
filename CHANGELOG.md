# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-24

### Added

- Initial release with five documentation pipeline capabilities:
  - `validate-requirements`: validates YAML requirement files against a JSON schema
  - `validate-documents`: validates Markdown documentation frontmatter and required sections
  - `generate-requirements-pdf`: generates a PDF from YAML requirement files using a Markdown template
  - `build-pdfs`: converts Markdown documentation directories and YAML requirements to PDFs
  - `traceability-matrix`: generates a requirements-vs-SIL traceability matrix in Markdown and optionally PDF
- GitHub composite action (`action.yml`) with feature-flag inputs for each capability
- Full test suite (unit tests for all modules)
- CI workflow: lint, type-check, unit tests, coverage, action smoke test
- Release automation via release-please
