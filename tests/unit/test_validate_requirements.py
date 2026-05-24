"""Unit tests for validate_requirements."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
import yaml

from project_documentation.validate_requirements import main


@pytest.fixture()
def tmp_schema(tmp_path: Path) -> Path:
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["id", "title", "shall"],
            "properties": {
                "id":    {"type": "string"},
                "title": {"type": "string"},
                "shall": {"type": "string"},
            },
            "additionalProperties": False,
        },
    }
    p = tmp_path / "requirement.schema.json"
    p.write_text(json.dumps(schema))
    return p


@pytest.fixture()
def tmp_requirements_dir(tmp_path: Path) -> Path:
    d = tmp_path / "requirements"
    d.mkdir()
    return d


def _write_yaml(directory: Path, name: str, content: object) -> Path:
    p = directory / name
    p.write_text(yaml.dump(content))
    return p


class TestValidRequirements:
    def test_valid_file_exits_zero(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        _write_yaml(
            tmp_requirements_dir,
            "foc.yaml",
            [{"id": "REQ-FOC-001", "title": "FOC loop", "shall": "The system shall..."}],
        )
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 0
        out = capsys.readouterr().out
        assert "foc.yaml" in out

    def test_empty_file_is_warned_not_failed(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        (tmp_requirements_dir / "empty.yaml").write_text("")
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 0
        assert "empty" in capsys.readouterr().out


class TestInvalidRequirements:
    def test_missing_field_exits_nonzero(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        _write_yaml(
            tmp_requirements_dir,
            "bad.yaml",
            [{"id": "REQ-001", "title": "Missing shall field"}],
        )
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 1
        assert "bad.yaml" in capsys.readouterr().out

    def test_extra_field_exits_nonzero(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_yaml(
            tmp_requirements_dir,
            "extra.yaml",
            [{"id": "REQ-001", "title": "T", "shall": "S", "unknown": "x"}],
        )
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 1

    def test_no_yaml_files_exits_zero(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 0

    def test_nested_requirements_are_found(
        self,
        tmp_schema: Path,
        tmp_requirements_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        sub = tmp_requirements_dir / "sub"
        sub.mkdir()
        _write_yaml(sub, "nested.yaml", [{"id": "REQ-002", "title": "T", "shall": "S"}])
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--schema", str(tmp_schema), "--requirements-dir", str(tmp_requirements_dir)],
        )
        assert main() == 0
        assert "nested.yaml" in capsys.readouterr().out


_VALID_DOC = textwrap.dedent("""\
    ---
    title: Test Architecture
    type: architecture
    status: draft
    version: "1.0"
    component: test
    ---

    ## Assumptions & Constraints

    Some constraints.

    ## System Overview

    Overview here.

    ## Component Decomposition

    Components here.

    ## Interfaces & Contracts

    Interfaces here.
""")
