# Usage Reference

`embedded-pro/project-documentation` is a GitHub composite action that runs
the documentation pipeline for embedded projects: it validates requirements
and design documents, generates PDFs, and produces a requirements traceability
matrix.

---

## Quick Start

```yaml
- uses: embedded-pro/project-documentation@main
  with:
    run-validate-requirements: 'true'
    schema-path: documentation/tools/requirement.schema.json
    requirements-dir: documentation/requirements
```

---

## Inputs

### Feature flags

| Input                          | Default   | Description                                              |
|-------------------------------|-----------|----------------------------------------------------------|
| `run-validate-requirements`   | `'false'` | Validate YAML requirement files against a JSON schema.  |
| `run-validate-documents`      | `'false'` | Validate Markdown docs against templates.               |
| `run-generate-requirements-pdf` | `'false'` | Generate a PDF from YAML requirement files.            |
| `run-build-documentation-pdfs` | `'false'` | Convert Markdown docs + YAML requirements to PDFs.    |
| `run-traceability-matrix`     | `'false'` | Generate a requirements traceability matrix.            |

### Validate requirements

| Input               | Default                                          | Description                        |
|--------------------|--------------------------------------------------|------------------------------------|
| `requirements-dir` | `documentation/requirements`                    | Directory containing YAML files.   |
| `schema-path`      | `documentation/tools/requirement.schema.json`   | JSON schema for validation.        |

### Validate documents

| Input            | Default           | Description                                                       |
|-----------------|-------------------|-------------------------------------------------------------------|
| `documents-dir` | `documentation`   | Root directory to search for Markdown documents.                  |
| `doc-type`      | `all`             | Filter: `architecture`, `design`, `theory`, or `all`.            |

### Generate requirements PDF

| Input                     | Default                              | Description                                   |
|--------------------------|--------------------------------------|-----------------------------------------------|
| `requirements-dir`       | `documentation/requirements`         | Directory containing YAML requirement files.  |
| `template-path`          | `documentation/templates/requirements.md` | Markdown template used by pandoc.        |
| `requirements-pdf-output`| `documentation/output/requirements.pdf`  | Output path for the PDF.                 |
| `upload-requirements-pdf`| `'false'`                            | If `'true'`, upload as a workflow artifact.   |

### Build documentation PDFs

| Input            | Default                                                              | Description                                         |
|-----------------|----------------------------------------------------------------------|-----------------------------------------------------|
| `version`       | `""`                                                                 | Release version used to name output files.          |
| `output-dir`    | `docs-pdf`                                                           | Output directory for PDFs.                          |
| `docs-dirs`     | `documentation/architecture documentation/design documentation/theory` | Space-separated doc directories.               |
| `requirements-dir` | `documentation/requirements`                                      | Requirements dir (included as appendix).            |
| `artifact-name` | `documentation-pdfs`                                                 | Name for the uploaded artifact.                     |

### Traceability matrix

| Input               | Default                                          | Description                                                       |
|--------------------|--------------------------------------------------|-------------------------------------------------------------------|
| `requirements-dir` | `documentation/requirements`                    | Directory containing YAML requirement files.                      |
| `features-dir`     | `integration_tests/software_in_the_loop/features` | Directory containing Gherkin `.feature` files.                 |
| `junit-xml`        | `""`                                             | Path to JUnit XML. If set, adds a test-status column.            |
| `matrix-output`    | `docs-pdf/traceability-matrix.md`               | Output path for the Markdown matrix.                             |
| `matrix-pdf-output`| `""`                                             | If set, also convert the matrix to a PDF at this path.           |

### Tooling

| Input             | Default  | Description                                                                            |
|------------------|----------|----------------------------------------------------------------------------------------|
| `python-version` | `3.11`   | Python version to use.                                                                 |
| `package-version`| `""`     | pip specifier for `project-documentation` (e.g. `==0.1.0`). Empty = latest from PyPI. |

---

## Outputs

| Output        | Description                                             |
|--------------|---------------------------------------------------------|
| `output-dir`  | Path to the directory containing generated PDF files.  |
| `matrix-path` | Path to the generated Markdown traceability matrix.    |

---

## Examples

### Validate all document types on every push

```yaml
on: [push, pull_request]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: embedded-pro/project-documentation@main
        with:
          run-validate-documents: 'true'
          documents-dir: documentation
          doc-type: all
```

### Full release pipeline

```yaml
- uses: embedded-pro/project-documentation@main
  with:
    run-validate-requirements:    'true'
    run-validate-documents:       'true'
    run-generate-requirements-pdf: 'true'
    run-build-documentation-pdfs:  'true'
    run-traceability-matrix:       'true'
    version: ${{ github.ref_name }}
    upload-requirements-pdf: 'true'
    junit-xml: sil-results/junit.xml
```

### Pin to a specific version

```yaml
- uses: embedded-pro/project-documentation@main
  with:
    run-validate-requirements: 'true'
    package-version: "==0.1.0"
```
