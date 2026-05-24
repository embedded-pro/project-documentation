"""Integration tests — exercise real CLI entry points end-to-end.

These tests call the installed CLI commands via subprocess so they exercise
the full path from argument parsing through file I/O.  PDF-generating tests
are skipped when pandoc is not available in the environment.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

# ── helpers ───────────────────────────────────────────────────────────────────

def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def _write_yaml(path: Path, content: object) -> None:
    path.write_text(yaml.dump(content))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content))


_PANDOC_AVAILABLE = shutil.which("pandoc") is not None
_skip_no_pandoc = pytest.mark.skipif(not _PANDOC_AVAILABLE, reason="pandoc not installed")

# ── validate-requirements ─────────────────────────────────────────────────────

class TestValidateRequirementsCLI:
    @pytest.fixture()
    def req_env(self, tmp_path: Path) -> dict[str, Path]:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        schema = tmp_path / "requirement.schema.json"
        schema.write_text(
            '{"type":"array","items":{"type":"object","required":["id","title","shall"],'
            '"properties":{"id":{"type":"string"},"title":{"type":"string"},"shall":{"type":"string"}},'
            '"additionalProperties":false}}'
        )
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Clarke", "shall": "The system shall..."}],
        )
        return {"req_dir": req_dir, "schema": schema}

    def test_valid_requirements_exits_zero(self, req_env: dict[str, Path]) -> None:
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_requirements",
                "--schema", str(req_env["schema"]),
                "--requirements-dir", str(req_env["req_dir"]),
            ]
        )
        assert result.returncode == 0
        assert "✓" in result.stdout

    def test_invalid_requirement_exits_nonzero(self, req_env: dict[str, Path]) -> None:
        _write_yaml(
            req_env["req_dir"] / "bad.yaml",
            [{"id": "REQ-001", "unknown_field": "oops"}],
        )
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_requirements",
                "--schema", str(req_env["schema"]),
                "--requirements-dir", str(req_env["req_dir"]),
            ]
        )
        assert result.returncode == 1
        assert "✗" in result.stdout

    def test_empty_dir_exits_zero(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "empty"
        req_dir.mkdir()
        schema = tmp_path / "s.json"
        schema.write_text('{"type":"array","items":{"type":"object"}}')
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_requirements",
                "--schema", str(schema),
                "--requirements-dir", str(req_dir),
            ]
        )
        assert result.returncode == 0


# ── validate-documents ────────────────────────────────────────────────────────

class TestValidateDocumentsCLI:
    _VALID_ARCHITECTURE = textwrap.dedent("""\
        ---
        title: FOC Architecture
        type: architecture
        status: draft
        version: "1.0"
        component: foc
        ---

        ## Assumptions & Constraints
        No heap.

        ## System Overview
        Overview.

        ## Component Decomposition
        - Clarke
        - Park

        ## Interfaces & Contracts
        All pure virtual.
    """)

    def test_valid_architecture_exits_zero(self, tmp_path: Path) -> None:
        _write_text(tmp_path / "arch.md", self._VALID_ARCHITECTURE)
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_documents",
                "--documents-dir", str(tmp_path),
                "--doc-type", "architecture",
            ]
        )
        assert result.returncode == 0

    def test_forbidden_code_block_exits_nonzero(self, tmp_path: Path) -> None:
        doc = self._VALID_ARCHITECTURE + "\n```cpp\nvoid foo(){}\n```\n"
        _write_text(tmp_path / "doc.md", doc)
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_documents",
                "--documents-dir", str(tmp_path),
                "--doc-type", "architecture",
            ]
        )
        assert result.returncode == 1

    def test_missing_section_exits_nonzero(self, tmp_path: Path) -> None:
        doc = textwrap.dedent("""\
            ---
            title: Incomplete
            type: architecture
            status: draft
            version: "1.0"
            component: foc
            ---

            ## Assumptions & Constraints
            Only one section.
        """)
        _write_text(tmp_path / "incomplete.md", doc)
        result = _run(
            [
                sys.executable, "-m", "project_documentation.validate_documents",
                "--documents-dir", str(tmp_path),
                "--doc-type", "architecture",
            ]
        )
        assert result.returncode == 1


# ── generate-traceability-matrix ──────────────────────────────────────────────

class TestTraceabilityMatrixCLI:
    def test_generates_matrix_markdown(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Clarke", "shall": "..."}],
        )
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        (features_dir / "foc.feature").write_text(
            "Feature: FOC\n  # REQ-FOC-001\n  Scenario: Clarke works\n    Given ...\n"
        )
        output = tmp_path / "matrix.md"

        result = _run(
            [
                sys.executable, "-m", "project_documentation.generate_traceability_matrix",
                "--requirements-dir", str(req_dir),
                "--features-dir", str(features_dir),
                "--output", str(output),
            ]
        )
        assert result.returncode == 0
        assert output.exists()
        content = output.read_text()
        assert "REQ-FOC-001" in content
        assert "Clarke works" in content

    def test_uncovered_requirement_listed(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Uncovered", "shall": "..."}],
        )
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        output = tmp_path / "matrix.md"

        result = _run(
            [
                sys.executable, "-m", "project_documentation.generate_traceability_matrix",
                "--requirements-dir", str(req_dir),
                "--features-dir", str(features_dir),
                "--output", str(output),
            ]
        )
        assert result.returncode == 0
        assert "Uncovered Requirements" in output.read_text()

    def test_coverage_summary_shows_percentage(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(req_dir / "foc.yaml", [{"id": "REQ-FOC-001", "title": "T", "shall": "S"}])
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        (features_dir / "foc.feature").write_text(
            "Feature: F\n  # REQ-FOC-001\n  Scenario: S1\n    Given ...\n"
        )
        output = tmp_path / "matrix.md"
        _run(
            [
                sys.executable, "-m", "project_documentation.generate_traceability_matrix",
                "--requirements-dir", str(req_dir),
                "--features-dir", str(features_dir),
                "--output", str(output),
            ]
        )
        assert "100%" in output.read_text()


# ── generate-requirements-pdf ─────────────────────────────────────────────────

@_skip_no_pandoc
class TestGenerateRequirementsPDFCLI:
    def test_generates_pdf_and_intermediate_md(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Clarke transform", "shall": "The system shall..."}],
        )
        template = tmp_path / "template.md"
        template.write_text("# Requirements\n\n")
        output = tmp_path / "out" / "requirements.pdf"

        result = _run(
            [
                sys.executable, "-m", "project_documentation.generate_requirements_pdf",
                "--requirements-dir", str(req_dir),
                "--template", str(template),
                "--output", str(output),
            ]
        )
        assert result.returncode == 0, result.stderr
        assert output.exists()
        assert output.with_suffix(".md").exists()

    def test_intermediate_markdown_contains_requirements(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-001", "title": "My Title", "shall": "The system shall do X."}],
        )
        template = tmp_path / "template.md"
        template.write_text("# Header\n\n")
        output = tmp_path / "out.pdf"

        _run(
            [
                sys.executable, "-m", "project_documentation.generate_requirements_pdf",
                "--requirements-dir", str(req_dir),
                "--template", str(template),
                "--output", str(output),
            ]
        )
        md = output.with_suffix(".md").read_text()
        assert "REQ-001" in md
        assert "My Title" in md


# ── build-documentation-pdfs ──────────────────────────────────────────────────

@_skip_no_pandoc
class TestBuildDocumentationPDFsCLI:
    _VALID_THEORY = textwrap.dedent("""\
        ---
        title: FOC Theory
        type: theory
        status: approved
        version: "1.0"
        component: foc
        ---

        ## Overview
        FOC overview.

        ## Mathematical Foundation
        $i_d = i_s \\cos\\theta$

        ## Numerical Properties
        Q15 fixed-point.
    """)

    def test_generates_pdf_from_markdown(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "theory"
        docs_dir.mkdir()
        _write_text(docs_dir / "foc.md", self._VALID_THEORY)
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        output_dir = tmp_path / "out"

        result = _run(
            [
                sys.executable, "-m", "project_documentation.build_documentation_pdfs",
                "--version", "v1.0",
                "--output-dir", str(output_dir),
                "--docs-dirs", str(docs_dir),
                "--requirements-dir", str(req_dir),
            ]
        )
        assert result.returncode == 0, result.stderr
        pdfs = list(output_dir.glob("*.pdf"))
        assert len(pdfs) >= 1
        assert any("theory-foc-v1.0.pdf" in p.name for p in pdfs)

    def test_output_filenames_have_no_e_foc_prefix(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "design"
        docs_dir.mkdir()
        _write_text(docs_dir / "clarke.md", "# Clarke\n\nDesign.")
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        output_dir = tmp_path / "out"

        _run(
            [
                sys.executable, "-m", "project_documentation.build_documentation_pdfs",
                "--version", "v2.0",
                "--output-dir", str(output_dir),
                "--docs-dirs", str(docs_dir),
                "--requirements-dir", str(req_dir),
            ]
        )
        for pdf in output_dir.glob("*.pdf"):
            assert not pdf.name.startswith("e_foc"), f"Unexpected e_foc prefix: {pdf.name}"
