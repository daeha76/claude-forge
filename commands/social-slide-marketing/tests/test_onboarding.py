"""Tests for onboarding.py — _collect_validation_issues() and _print_validation_results()."""

import json
import pytest
import onboarding as ob


class TestCollectValidationIssues:
    """Test _collect_validation_issues() extraction."""

    def test_valid_config_no_issues(self, tmp_config):
        _, config = tmp_config
        issues, warnings, env_vars, pillow_ok = ob._collect_validation_issues(config)
        assert len(issues) == 0 or all("~/.env" in i or "Pillow" in i for i in issues)

    def test_empty_app_name_raises_issue(self):
        config = {
            "app": {"name": "", "description": "x", "audience": "x", "problem": "x"},
            "postiz": {"apiKey": "k", "integrationIds": {"tiktok": "t", "instagram": "i"}},
        }
        issues, _, _, _ = ob._collect_validation_issues(config)
        assert any("app.name" in i for i in issues)

    def test_missing_all_required_fields(self):
        config = {
            "app": {},
            "postiz": {"apiKey": "", "integrationIds": {}},
        }
        issues, _, _, _ = ob._collect_validation_issues(config)
        assert any("app.name" in i for i in issues)
        assert any("app.description" in i for i in issues)
        assert any("app.audience" in i for i in issues)
        assert any("app.problem" in i for i in issues)
        assert any("postiz.apiKey" in i for i in issues)
        assert any("tiktok" in i for i in issues)

    def test_optional_fields_generate_warnings(self):
        config = {
            "app": {
                "name": "App", "description": "Desc",
                "audience": "Dev", "problem": "Bug",
                "differentiator": "", "url": "", "category": "",
            },
            "postiz": {"apiKey": "k", "integrationIds": {"tiktok": "t"}},
        }
        issues, warnings, _, _ = ob._collect_validation_issues(config)
        assert any("differentiator" in w for w in warnings)
        assert any("url" in w for w in warnings)
        assert any("category" in w for w in warnings)

    def test_missing_instagram_is_warning_not_issue(self):
        config = {
            "app": {"name": "A", "description": "D", "audience": "U", "problem": "P"},
            "postiz": {"apiKey": "k", "integrationIds": {"tiktok": "t"}},
        }
        issues, warnings, _, _ = ob._collect_validation_issues(config)
        assert not any("instagram" in i for i in issues)
        assert any("instagram" in w for w in warnings)

    def test_returns_four_element_tuple(self, tmp_config):
        _, config = tmp_config
        result = ob._collect_validation_issues(config)
        assert len(result) == 4
        issues, warnings, env_vars, pillow_ok = result
        assert isinstance(issues, list)
        assert isinstance(warnings, list)
        assert isinstance(env_vars, dict)
        assert isinstance(pillow_ok, bool)

    def test_pillow_detected(self, tmp_config):
        _, config = tmp_config
        _, _, _, pillow_ok = ob._collect_validation_issues(config)
        assert pillow_ok is True


class TestPrintValidationResults:
    """Test _print_validation_results() output and return value."""

    def test_returns_100_when_no_issues(self, capsys):
        env_vars = {"GEMINI_API_KEY": True}
        pct = ob._print_validation_results([], [], env_vars, True)
        assert pct == 100
        captured = capsys.readouterr()
        assert "READY" in captured.out

    def test_returns_less_than_100_with_issues(self, capsys):
        pct = ob._print_validation_results(
            ["app.name is empty"], [], {}, True
        )
        assert pct < 100
        captured = capsys.readouterr()
        assert "INCOMPLETE" in captured.out

    def test_prints_issues(self, capsys):
        ob._print_validation_results(
            ["app.name is empty", "postiz.apiKey is empty"], [], {}, True
        )
        captured = capsys.readouterr()
        assert "app.name is empty" in captured.out
        assert "postiz.apiKey is empty" in captured.out

    def test_prints_warnings(self, capsys):
        ob._print_validation_results(
            [], ["app.url is empty (recommended)"], {}, True
        )
        captured = capsys.readouterr()
        assert "app.url is empty" in captured.out

    def test_prints_pillow_status(self, capsys):
        ob._print_validation_results([], [], {}, True)
        captured = capsys.readouterr()
        assert "Pillow: OK" in captured.out

        ob._print_validation_results([], [], {}, False)
        captured = capsys.readouterr()
        assert "Pillow: MISSING" in captured.out


class TestValidateConfig:
    """Test the orchestrator validate_config()."""

    def test_missing_config_returns_invalid(self, monkeypatch, tmp_path):
        monkeypatch.setattr(ob, "CONFIG_PATH", tmp_path / "nonexistent.json")
        result = ob.validate_config()
        assert result["valid"] is False

    def test_valid_config_returns_expected_keys(self, monkeypatch, tmp_config):
        config_path, _ = tmp_config
        from pathlib import Path
        monkeypatch.setattr(ob, "CONFIG_PATH", Path(config_path))
        result = ob.validate_config()
        assert "valid" in result
        assert "issues" in result
        assert "warnings" in result
        assert "completion_pct" in result
