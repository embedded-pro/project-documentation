"""Unit tests for validate_documents."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from project_documentation.validate_documents import main


def _write_doc(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


_VALID_ARCHITECTURE = textwrap.dedent("""\
    ---
    title: FOC Architecture
    type: architecture
    status: draft
    version: "1.0"
    component: foc
    ---

    ## Assumptions & Constraints

    No heap allocation.

    ## System Overview

    The FOC system performs field-oriented control.

    ## Component Decomposition

    - Clarke transform
    - Park transform

    ## Interfaces & Contracts

    All interfaces are pure virtual.
""")

_VALID_DESIGN = textwrap.dedent("""\
    ---
    title: Clarke Transform Design
    type: design
    status: approved
    version: "2.0"
    component: foc
    ---

    ## Responsibilities

    Converts 3-phase currents to 2-phase.

    ## Component Details

    Uses the standard Clarke transform equations.

    ## Interfaces

    Input: ia, ib, ic. Output: alpha, beta.
""")

_VALID_THEORY = textwrap.dedent("""\
    ---
    title: FOC Theory
    type: theory
    status: approved
    version: "1.0"
    component: foc
    ---

    ## Overview

    Field-Oriented Control (FOC) theory.

    ## Mathematical Foundation

    $i_d = i_s \\cos(\\theta)$

    ## Numerical Properties

    Fixed-point arithmetic with Q15 representation.
""")


class TestValidDocuments:
    def test_valid_architecture_exits_zero(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_doc(tmp_path, "arch.md", _VALID_ARCHITECTURE)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 0

    def test_valid_design_exits_zero(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_doc(tmp_path, "design.md", _VALID_DESIGN)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "design"]
        )
        assert main() == 0

    def test_valid_theory_exits_zero(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_doc(tmp_path, "theory.md", _VALID_THEORY)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "theory"]
        )
        assert main() == 0

    def test_wrong_type_is_skipped(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Architecture doc should be silently skipped when filtering for design."""
        _write_doc(tmp_path, "arch.md", _VALID_ARCHITECTURE)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "design"]
        )
        assert main() == 0


class TestMissingFrontmatter:
    def test_no_frontmatter_warns_in_all_mode(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        _write_doc(tmp_path, "plain.md", "# Just a heading\n\nNo frontmatter.")
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "all"]
        )
        assert main() == 0
        assert "⚠" in capsys.readouterr().out

    def test_missing_required_field_exits_nonzero(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        doc = textwrap.dedent("""\
            ---
            title: Missing Fields
            type: architecture
            ---

            ## Assumptions & Constraints
            ## System Overview
            ## Component Decomposition
            ## Interfaces & Contracts
        """)
        _write_doc(tmp_path, "bad.md", doc)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 1


class TestForbiddenContent:
    def test_code_block_in_architecture_fails(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        doc = _VALID_ARCHITECTURE + "\n```cpp\nvoid foo() {}\n```\n"
        _write_doc(tmp_path, "doc.md", doc)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 1

    def test_image_reference_in_architecture_fails(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        doc = _VALID_ARCHITECTURE + "\n![diagram](path/to/image.png)\n"
        _write_doc(tmp_path, "doc.md", doc)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 1

    def test_mermaid_block_is_allowed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        doc = _VALID_ARCHITECTURE + "\n```mermaid\ngraph TD; A-->B\n```\n"
        _write_doc(tmp_path, "doc.md", doc)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 0


class TestMissingRequiredSections:
    def test_missing_section_fails(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        doc = textwrap.dedent("""\
            ---
            title: Incomplete Architecture
            type: architecture
            status: draft
            version: "1.0"
            component: foc
            ---

            ## Assumptions & Constraints

            Some constraints.

            ## System Overview

            Overview.
        """)
        _write_doc(tmp_path, "incomplete.md", doc)
        monkeypatch.setattr(
            "sys.argv", ["prog", "--documents-dir", str(tmp_path), "--doc-type", "architecture"]
        )
        assert main() == 1
