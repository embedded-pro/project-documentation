"""Unit tests for generate_traceability_matrix."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from project_documentation.generate_traceability_matrix import (
    generate_matrix,
    load_feature_mapping,
    load_requirements,
)


@pytest.fixture()
def requirements_dir(tmp_path: Path) -> Path:
    d = tmp_path / "requirements"
    d.mkdir()
    return d


@pytest.fixture()
def features_dir(tmp_path: Path) -> Path:
    d = tmp_path / "features"
    d.mkdir()
    return d


def _write_yaml(directory: Path, name: str, content: object) -> None:
    (directory / name).write_text(yaml.dump(content))


def _write_feature(directory: Path, name: str, content: str) -> None:
    (directory / name).write_text(content)


class TestLoadRequirements:
    def test_loads_single_file(self, requirements_dir: Path) -> None:
        _write_yaml(
            requirements_dir,
            "foc.yaml",
            [
                {"id": "REQ-FOC-001", "title": "Clarke transform", "shall": "The system shall..."},
                {"id": "REQ-FOC-002", "title": "Park transform", "shall": "The system shall..."},
            ],
        )
        reqs = load_requirements(requirements_dir)
        assert "REQ-FOC-001" in reqs
        assert "REQ-FOC-002" in reqs
        assert reqs["REQ-FOC-001"]["domain"] == "foc"

    def test_empty_directory_returns_empty(self, requirements_dir: Path) -> None:
        assert load_requirements(requirements_dir) == {}

    def test_skips_non_list_yaml(self, requirements_dir: Path) -> None:
        (requirements_dir / "bad.yaml").write_text("key: value\n")
        assert load_requirements(requirements_dir) == {}


class TestLoadFeatureMapping:
    def test_maps_scenario_to_requirement(self, features_dir: Path) -> None:
        _write_feature(
            features_dir,
            "foc.feature",
            "Feature: FOC\n  # REQ-FOC-001\n  Scenario: Clarke transform works\n    Given ...\n",
        )
        mapping = load_feature_mapping(features_dir)
        assert "REQ-FOC-001" in mapping
        assert "Clarke transform works" in mapping["REQ-FOC-001"]

    def test_multiple_reqs_on_one_scenario(self, features_dir: Path) -> None:
        _write_feature(
            features_dir,
            "multi.feature",
            "Feature: Multi\n  # REQ-FOC-001, REQ-FOC-002\n  Scenario: Combined check\n    Given ...\n",
        )
        mapping = load_feature_mapping(features_dir)
        assert "Combined check" in mapping.get("REQ-FOC-001", [])
        assert "Combined check" in mapping.get("REQ-FOC-002", [])

    def test_empty_directory_returns_empty(self, features_dir: Path) -> None:
        assert load_feature_mapping(features_dir) == {}


class TestGenerateMatrix:
    def test_covered_requirement_in_table(self) -> None:
        reqs = {
            "REQ-FOC-001": {"id": "REQ-FOC-001", "title": "Clarke", "shall": "...", "domain": "foc"}
        }
        feature_map = {"REQ-FOC-001": ["Clarke transform works"]}
        md = generate_matrix(reqs, feature_map, {})
        assert "REQ-FOC-001" in md
        assert "Clarke transform works" in md

    def test_uncovered_requirement_listed(self) -> None:
        reqs = {
            "REQ-FOC-001": {"id": "REQ-FOC-001", "title": "Clarke", "shall": "...", "domain": "foc"}
        }
        md = generate_matrix(reqs, {}, {})
        assert "_not covered_" in md
        assert "Uncovered Requirements" in md

    def test_coverage_summary_present(self) -> None:
        reqs = {
            "REQ-FOC-001": {"id": "REQ-FOC-001", "title": "T", "shall": "S", "domain": "foc"}
        }
        md = generate_matrix(reqs, {"REQ-FOC-001": ["Scenario A"]}, {})
        assert "Coverage Summary" in md
        assert "100%" in md

    def test_status_column_present_with_junit(self) -> None:
        reqs = {
            "REQ-FOC-001": {"id": "REQ-FOC-001", "title": "T", "shall": "S", "domain": "foc"}
        }
        feature_map = {"REQ-FOC-001": ["Scenario A"]}
        junit = {"Scenario A": "pass"}
        md = generate_matrix(reqs, feature_map, junit)
        assert "Status" in md
        assert "PASS" in md

    def test_fail_status_propagates(self) -> None:
        reqs = {
            "REQ-FOC-001": {"id": "REQ-FOC-001", "title": "T", "shall": "S", "domain": "foc"}
        }
        feature_map = {"REQ-FOC-001": ["Scenario A"]}
        junit = {"Scenario A": "fail"}
        md = generate_matrix(reqs, feature_map, junit)
        assert "FAIL" in md
