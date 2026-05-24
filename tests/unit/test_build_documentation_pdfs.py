"""Unit tests for build_documentation_pdfs."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from project_documentation.build_documentation_pdfs import (
    _requirement_to_markdown,
    convert_markdown_dirs,
    convert_requirements,
)


def _write_yaml(path: Path, content: object) -> None:
    path.write_text(yaml.dump(content))


class TestRequirementToMarkdown:
    def test_full_requirement(self) -> None:
        req = {"id": "REQ-FOC-001", "title": "Clarke transform", "shall": "The system shall..."}
        md = _requirement_to_markdown(req)
        assert "## REQ-FOC-001: Clarke transform" in md
        assert "The system shall..." in md

    def test_missing_fields_produce_empty_strings(self) -> None:
        md = _requirement_to_markdown({})
        assert "## :" in md  # empty id: empty title

    def test_no_shall_omits_body(self) -> None:
        md = _requirement_to_markdown({"id": "REQ-001", "title": "T", "shall": ""})
        assert "REQ-001" in md
        lines = [ln for ln in md.splitlines() if ln.strip()]
        assert len(lines) == 1  # only the heading


class TestConvertMarkdownDirs:
    def test_converts_md_files_in_dir(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "architecture"
        docs_dir.mkdir()
        (docs_dir / "overview.md").write_text("# Overview\n")
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc",
            return_value=True,
        ) as mock_pandoc:
            convert_markdown_dirs([str(docs_dir)], "v1.0", output_dir)

        assert mock_pandoc.call_count == 1
        out_path = mock_pandoc.call_args[0][0]
        assert "architecture-overview-v1.0.pdf" in str(out_path)

    def test_no_e_foc_prefix_in_output(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "design"
        docs_dir.mkdir()
        (docs_dir / "foc.md").write_text("# FOC\n")
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc",
            return_value=True,
        ) as mock_pandoc:
            convert_markdown_dirs([str(docs_dir)], "v2.0", output_dir)

        out_path = mock_pandoc.call_args[0][0]
        assert not out_path.name.startswith("e_foc"), f"Unexpected e_foc prefix: {out_path.name}"
        assert "design-foc-v2.0.pdf" == out_path.name

    def test_missing_dir_is_skipped(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc"
        ) as mock_pandoc:
            convert_markdown_dirs([str(tmp_path / "nonexistent")], "v1.0", output_dir)
        mock_pandoc.assert_not_called()


class TestConvertRequirements:
    def test_produces_requirements_pdf(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        _write_yaml(
            req_dir / "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Clarke", "shall": "The system shall..."}],
        )
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc",
            return_value=True,
        ) as mock_pandoc:
            convert_requirements(req_dir, "v1.2", output_dir)

        assert mock_pandoc.call_count == 1
        out_path = str(mock_pandoc.call_args[0][0])
        assert "requirements-v1.2.pdf" in out_path
        assert "e_foc" not in out_path

    def test_empty_requirements_dir_skips_pandoc(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc"
        ) as mock_pandoc:
            convert_requirements(req_dir, "v1.0", output_dir)

        mock_pandoc.assert_not_called()

    def test_non_list_yaml_is_skipped(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        (req_dir / "bad.yaml").write_text("key: value\n")
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch(
            "project_documentation.build_documentation_pdfs._run_pandoc"
        ) as mock_pandoc:
            convert_requirements(req_dir, "v1.0", output_dir)

        mock_pandoc.assert_not_called()
