"""Tests for daily_report.py — _collect_report_data(), _build_report_lines(), and helpers."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import daily_report as dr


class TestDiagnoseFunnel:
    """Test diagnose_funnel() pure function."""

    def test_low_views_bottleneck(self):
        result = dr.diagnose_funnel(5000, 100, 10)
        assert result["bottleneck"] == "views"
        assert "도달" in result["diagnosis"]

    def test_low_ctr_bottleneck(self):
        result = dr.diagnose_funnel(50000, 200, 10)
        assert result["bottleneck"] == "cta"

    def test_low_conversion_bottleneck(self):
        result = dr.diagnose_funnel(50000, 2000, 10)
        assert result["bottleneck"] == "landing"

    def test_healthy_funnel(self):
        result = dr.diagnose_funnel(50000, 2000, 200)
        assert result["bottleneck"] == "none"

    def test_zero_views(self):
        result = dr.diagnose_funnel(0, 0, 0)
        assert result["bottleneck"] == "views"
        assert result["metrics"]["ctr"] == 0
        assert result["metrics"]["conversion_rate"] == 0

    def test_metrics_included(self):
        result = dr.diagnose_funnel(100000, 5000, 500)
        metrics = result["metrics"]
        assert metrics["total_views"] == 100000
        assert metrics["link_clicks"] == 5000
        assert metrics["conversions"] == 500
        assert metrics["ctr"] == 5.0
        assert metrics["conversion_rate"] == 10.0


class TestGetFunnelTotals:
    """Test _get_funnel_totals() pure function."""

    def test_sums_from_performances(self):
        perfs = [
            {"views": 1000, "link_clicks": 50, "conversions": 5},
            {"views": 2000, "link_clicks": 100, "conversions": 10},
        ]
        views, clicks, conversions = dr._get_funnel_totals(perfs, 0, 0)
        assert views == 3000
        assert clicks == 150
        assert conversions == 15

    def test_manual_overrides(self):
        perfs = [{"views": 1000, "link_clicks": 50, "conversions": 5}]
        views, clicks, conversions = dr._get_funnel_totals(perfs, 999, 99)
        assert views == 1000
        assert clicks == 999
        assert conversions == 99

    def test_empty_performances(self):
        views, clicks, conversions = dr._get_funnel_totals([], 0, 0)
        assert views == 0
        assert clicks == 0
        assert conversions == 0


class TestBuildReportLines:
    """Test _build_report_lines() formatting."""

    def _make_data(self, analytics=None, hook_analysis=None):
        return {
            "analytics": analytics or [],
            "hook_analysis": hook_analysis or {
                "top_hooks": [], "worst_hooks": [],
                "avg_views": 0, "avg_engagement": 0, "total_posts": 0,
            },
            "cta_suggestions": [],
            "hook_suggestions": [],
            "funnel_result": {
                "diagnosis": "test", "bottleneck": "none",
                "metrics": {"total_views": 0, "link_clicks": 0,
                            "conversions": 0, "ctr": 0, "conversion_rate": 0},
            },
            "new_learnings": [],
        }

    def test_returns_list_of_strings(self):
        data = self._make_data()
        lines = dr._build_report_lines("일일", 3, data)
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

    def test_contains_report_header(self):
        data = self._make_data()
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "일일 리포트" in joined
        assert "최근 3일" in joined

    def test_contains_weekly_header(self):
        data = self._make_data()
        lines = dr._build_report_lines("주간", 7, data)
        joined = "\n".join(lines)
        assert "주간 리포트" in joined
        assert "최근 7일" in joined

    def test_empty_analytics_shows_no_data_message(self):
        data = self._make_data(analytics=[])
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "데이터 없음" in joined

    def test_analytics_table_rendered(self, sample_analytics):
        data = self._make_data(analytics=sample_analytics)
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "포스트" in joined
        assert "조회수" in joined

    def test_funnel_section_included(self):
        data = self._make_data()
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "퍼널 진단" in joined

    def test_hook_summary_included(self, sample_hook_analysis):
        data = self._make_data(hook_analysis=sample_hook_analysis)
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "훅 성과 요약" in joined
        assert "40,000" in joined

    def test_footer_included(self):
        data = self._make_data()
        lines = dr._build_report_lines("일일", 3, data)
        joined = "\n".join(lines)
        assert "social-slide-marketing" in joined


class TestBuildFunnelSection:
    """Test _build_funnel_section() helper."""

    def test_contains_metrics(self):
        funnel = {
            "diagnosis": "퍼널 건강", "bottleneck": "none",
            "metrics": {"total_views": 50000, "link_clicks": 2000,
                        "conversions": 200, "ctr": 4.0, "conversion_rate": 10.0},
        }
        lines = dr._build_funnel_section(funnel)
        joined = "\n".join(lines)
        assert "50,000" in joined
        assert "2,000" in joined
        assert "4.0%" in joined


class TestBuildLearningsSection:
    """Test _build_learnings_section() helper."""

    def test_no_learnings_file(self, monkeypatch, tmp_path):
        monkeypatch.setattr(dr, "LEARNINGS_PATH", tmp_path / "nonexistent.json")
        lines = dr._build_learnings_section()
        joined = "\n".join(lines)
        assert "학습 기록 없음" in joined


class TestSuggestCtaRotation:
    """Test suggest_cta_rotation() pure function."""

    def test_fix_cta_gets_suggestions(self):
        analytics = [
            {"title": "Post 1", "diagnosis": {"diagnosis": "FIX CTA"}},
        ]
        result = dr.suggest_cta_rotation(analytics)
        assert len(result) == 1
        assert "높은 조회수" in result[0]["current_issue"]

    def test_scale_it_gets_suggestions(self):
        analytics = [
            {"title": "Post 1", "diagnosis": {"diagnosis": "SCALE IT"}},
        ]
        result = dr.suggest_cta_rotation(analytics)
        assert len(result) == 1

    def test_other_diagnosis_no_suggestions(self):
        analytics = [
            {"title": "Post 1", "diagnosis": {"diagnosis": "FULL RESET"}},
        ]
        result = dr.suggest_cta_rotation(analytics)
        assert len(result) == 0

    def test_empty_analytics(self):
        assert dr.suggest_cta_rotation([]) == []


class TestAutoGenerateHookVariations:
    """Test auto_generate_hook_variations() pure function."""

    def test_returns_three_variations(self):
        result = dr.auto_generate_hook_variations("이 앱 써봤는데 인생 바뀜")
        assert len(result) == 3

    def test_empty_input(self):
        assert dr.auto_generate_hook_variations("") == []

    def test_none_input(self):
        assert dr.auto_generate_hook_variations(None) == []

    def test_variations_are_strings(self):
        result = dr.auto_generate_hook_variations("I found this app")
        assert all(isinstance(v, str) for v in result)

    def test_variations_differ_from_original(self):
        original = "이 앱 써봤는데 인생 바뀜"
        result = dr.auto_generate_hook_variations(original)
        for var in result:
            assert var != original
