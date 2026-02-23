"""Tests for check_analytics.py — diagnose_post() and load_config()."""

import json
import pytest
import check_analytics as ca


class TestDiagnosePost:
    """Test all 6 diagnostic paths including the new BOOST case."""

    def test_scale_it_high_views_high_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["scale_it"])
        assert result["diagnosis"] == "SCALE IT"
        assert result["priority"] == "high"

    def test_fix_cta_high_views_low_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["fix_cta"])
        assert result["diagnosis"] == "FIX CTA"
        assert result["priority"] == "medium"

    def test_boost_medium_views_high_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["boost"])
        assert result["diagnosis"] == "BOOST"
        assert result["priority"] == "medium"
        assert "프로모션" in result["action"]

    def test_fix_hooks_low_views_high_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["fix_hooks"])
        assert result["diagnosis"] == "FIX HOOKS"
        assert result["priority"] == "medium"

    def test_optimize_medium_views_low_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["optimize"])
        assert result["diagnosis"] == "OPTIMIZE"
        assert result["priority"] == "low"

    def test_full_reset_low_views_low_engagement(self, sample_metrics):
        result = ca.diagnose_post(sample_metrics["full_reset"])
        assert result["diagnosis"] == "FULL RESET"
        assert result["priority"] == "high"

    def test_zero_views_returns_full_reset(self):
        result = ca.diagnose_post({"views": 0, "likes": 0, "comments": 0, "shares": 0})
        assert result["diagnosis"] == "FULL RESET"

    def test_zero_views_with_engagement_returns_full_reset(self):
        result = ca.diagnose_post({"views": 0, "likes": 10, "comments": 5, "shares": 2})
        assert result["diagnosis"] == "FULL RESET"

    def test_boost_boundary_10k_views(self):
        metrics = {"views": 10000, "likes": 400, "comments": 100, "shares": 50}
        result = ca.diagnose_post(metrics)
        assert result["diagnosis"] == "BOOST"

    def test_boost_boundary_49999_views(self):
        metrics = {"views": 49999, "likes": 2000, "comments": 500, "shares": 300}
        result = ca.diagnose_post(metrics)
        assert result["diagnosis"] == "BOOST"

    def test_scale_it_boundary_50k_views(self):
        metrics = {"views": 50000, "likes": 2000, "comments": 500, "shares": 300}
        result = ca.diagnose_post(metrics)
        assert result["diagnosis"] == "SCALE IT"

    def test_optimize_medium_views_just_under_3pct(self):
        metrics = {"views": 20000, "likes": 400, "comments": 100, "shares": 90}
        result = ca.diagnose_post(metrics)
        assert result["diagnosis"] == "OPTIMIZE"

    def test_result_always_has_required_keys(self, sample_metrics):
        for key, metrics in sample_metrics.items():
            result = ca.diagnose_post(metrics)
            assert "diagnosis" in result
            assert "action" in result
            assert "priority" in result


class TestLoadConfigCheckAnalytics:
    """Test load_config() error handling in check_analytics.py."""

    def test_load_valid_config(self, tmp_config):
        config_path, expected = tmp_config
        result = ca.load_config(config_path)
        assert result["app"]["name"] == "TestApp"
        assert result["postiz"]["apiKey"] == "test-api-key"

    def test_load_missing_config_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Config not found"):
            ca.load_config(str(tmp_path / "nonexistent.json"))

    def test_load_invalid_json_raises_value_error(self, tmp_invalid_json):
        with pytest.raises(ValueError, match="Invalid JSON"):
            ca.load_config(tmp_invalid_json)

    def test_load_empty_json_raises_value_error(self, tmp_path):
        empty = tmp_path / "empty.json"
        empty.write_text("")
        with pytest.raises(ValueError, match="Invalid JSON"):
            ca.load_config(str(empty))


class TestDetectHookFormula:
    """Test hook formula pattern detection."""

    def test_person_conflict(self):
        assert ca.detect_hook_formula("I found this amazing app") == "personConflict"

    def test_discovery(self):
        assert ca.detect_hook_formula("Stop using Excel") == "discovery"

    def test_pov(self):
        assert ca.detect_hook_formula("이 앱 써봤는데 진짜 좋음") == "pov"

    def test_command(self):
        assert ca.detect_hook_formula("This app will change your life") == "command"

    def test_social_proof(self):
        assert ca.detect_hook_formula("90% of people don't know") == "socialProof"

    def test_unknown(self):
        assert ca.detect_hook_formula("hello world") == "unknown"

    def test_empty_string(self):
        assert ca.detect_hook_formula("") == "unknown"

    def test_none_input(self):
        assert ca.detect_hook_formula(None) == "unknown"
