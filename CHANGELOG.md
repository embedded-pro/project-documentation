# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0](https://github.com/embedded-pro/project-documentation/compare/v0.2.0...v0.3.0) (2026-05-24)


### Features

* integration tests, unit tests for all modules, codeql, fix pdf prefix and engine ([62c3fcc](https://github.com/embedded-pro/project-documentation/commit/62c3fcc4bc9f575a562b7377358e0093e2232596))


### Bug Fixes

* add lmodern to LaTeX install for lmodern.sty ([54fca1c](https://github.com/embedded-pro/project-documentation/commit/54fca1cb9925af16e53bd9d2640d1285560d295b))
* add lmodern to LaTeX install for lmodern.sty ([df9b912](https://github.com/embedded-pro/project-documentation/commit/df9b9120a2be16def01b465964a8543bcbe76728))
* rewrite yoda condition in test (SIM300) ([714e373](https://github.com/embedded-pro/project-documentation/commit/714e373c832189bdc19534fe827fb605fb87421f))
* use REQ-FOC-001 format in traceability test (matches REQ-[A-Z]+-\d+ regex) ([5dd98cc](https://github.com/embedded-pro/project-documentation/commit/5dd98ccc3e04a9ced57aa8102ae3b1f64b8332c5))

## [0.2.0](https://github.com/embedded-pro/project-documentation/compare/v0.1.0...v0.2.0) (2026-05-24)


### Features

* initial project-documentation v0.1.0 ([cc9e17f](https://github.com/embedded-pro/project-documentation/commit/cc9e17fe8bfccbaaf58b27a226e68a851e251769))


### Bug Fixes

* add missing type annotations to satisfy mypy strict ([358f36a](https://github.com/embedded-pro/project-documentation/commit/358f36ad6cd173ff458b2d2bf4353159afef3897))
* sort imports to satisfy ruff I001 ([5b01b77](https://github.com/embedded-pro/project-documentation/commit/5b01b77031a28aa93342da2c60cb299ed0d14ffa))

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
