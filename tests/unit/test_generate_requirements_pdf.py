"""Unit tests for generate_requirements_pdf._build_markdown."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from project_documentation.generate_requirements_pdf import _build_markdown, main


def _write_yaml(directory: Path, name: str, content: object) -> None:
    (directory / name).write_text(yaml.dump(content))


class TestBuildMarkdown:
    def test_prepends_template(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "reqs"
        req_dir.mkdir()
        _write_yaml(
            req_dir,
            "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "Clarke", "shall": "The system shall..."}],
        )
        md = _build_markdown("# Header\n\n", list(req_dir.glob("*.yaml")))
        assert md.startswith("# Header\n\n")

    def test_section_title_from_parent_dir(self, tmp_path: Path) -> None:
        sub = tmp_path / "foc-control"
        sub.mkdir()
        _write_yaml(
            sub,
            "req.yaml",
            [{"id": "REQ-001", "title": "T", "shall": "S"}],
        )
        md = _build_markdown("", list(sub.glob("*.yaml")))
        assert "## Foc Control" in md

    def test_requirement_heading_and_body(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "reqs"
        req_dir.mkdir()
        _write_yaml(
            req_dir,
            "reqs.yaml",
            [{"id": "REQ-001", "title": "My Title", "shall": "The system shall do X."}],
        )
        md = _build_markdown("", list(req_dir.glob("*.yaml")))
        assert "### REQ-001: My Title" in md
        assert "The system shall do X." in md

    def test_empty_yaml_file_is_skipped(self, tmp_path: Path) -> None:
        req_dir = tmp_path / "reqs"
        req_dir.mkdir()
        (req_dir / "empty.yaml").write_text("")
        md = _build_markdown("template\n", list(req_dir.glob("*.yaml")))
        assert md == "template\n"

    def test_multiple_files_sorted_by_section(self, tmp_path: Path) -> None:
        for name in ("z-module", "a-module"):
            sub = tmp_path / name
            sub.mkdir()
            _write_yaml(sub, "r.yaml", [{"id": f"REQ-{name}", "title": "T", "shall": "S"}])
        files = sorted(tmp_path.rglob("*.yaml"))
        md = _build_markdown("", files)
        a_pos = md.index("A Module")
        z_pos = md.index("Z Module")
        assert a_pos < z_pos


class TestMain:
    def test_calls_pandoc_with_pdflatex(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        req_dir = tmp_path / "reqs"
        req_dir.mkdir()
        _write_yaml(
            req_dir,
            "foc.yaml",
            [{"id": "REQ-001", "title": "T", "shall": "S"}],
        )
        template = tmp_path / "template.md"
        template.write_text("# Requirements\n\n")
        output = tmp_path / "out" / "requirements.pdf"

        monkeypatch.setattr(
            "sys.argv",
            [
                "prog",
                "--requirements-dir", str(req_dir),
                "--template", str(template),
                "--output", str(output),
            ],
        )

        mock_run = MagicMock(return_value=MagicMock(returncode=0))
        with patch("subprocess.run", mock_run):
            main()

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "pandoc" in cmd
        assert "--pdf-engine=pdflatex" in cmd
        assert str(output) in cmd

    def test_intermediate_markdown_written(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        req_dir = tmp_path / "reqs"
        req_dir.mkdir()
        _write_yaml(req_dir, "foc.yaml", [{"id": "REQ-001", "title": "T", "shall": "S"}])
        template = tmp_path / "tmpl.md"
        template.write_text("# Header\n")
        output = tmp_path / "out.pdf"

        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--requirements-dir", str(req_dir), "--template", str(template), "--output", str(output)],
        )

        with patch("subprocess.run", MagicMock()):
            main()

        md_path = output.with_suffix(".md")
        assert md_path.exists()
        content = md_path.read_text()
        assert "# Header" in content
        assert "REQ-001" in content
