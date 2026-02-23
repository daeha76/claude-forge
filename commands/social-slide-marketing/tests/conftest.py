"""Shared fixtures for social-slide-marketing tests."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path so we can import them
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def tmp_config(tmp_path):
    """Create a valid temporary config file."""
    config = {
        "app": {
            "name": "TestApp",
            "description": "A test application",
            "audience": "developers",
            "problem": "testing is hard",
            "differentiator": "AI-powered",
            "url": "https://test.app",
            "category": "productivity",
            "isMobileApp": False,
        },
        "postiz": {
            "apiKey": "test-api-key",
            "integrationIds": {
                "tiktok": "tiktok-123",
                "instagram": "ig-456",
            },
        },
        "posting": {
            "privacyLevel": "SELF_ONLY",
            "schedule": ["07:30", "16:30"],
            "crossPost": ["instagram"],
            "autoAddMusic": True,
            "timezone": "Asia/Seoul",
            "hookRegister": "diary",
            "ctaType": "link_in_bio",
        },
        "conversion": {
            "enabled": True,
            "trackingMethod": "manual",
            "linkClickSource": "bitly",
            "notes": "",
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config, indent=2))
    return str(config_path), config


@pytest.fixture
def tmp_invalid_json(tmp_path):
    """Create a config file with invalid JSON."""
    config_path = tmp_path / "bad_config.json"
    config_path.write_text("{invalid json content")
    return str(config_path)


@pytest.fixture
def sample_metrics():
    """Sample post metrics for diagnose_post tests."""
    return {
        "scale_it": {"views": 80000, "likes": 3000, "comments": 500, "shares": 200},
        "fix_cta": {"views": 60000, "likes": 500, "comments": 50, "shares": 20},
        "boost": {"views": 30000, "likes": 1200, "comments": 300, "shares": 100},
        "fix_hooks": {"views": 5000, "likes": 200, "comments": 80, "shares": 30},
        "optimize": {"views": 20000, "likes": 200, "comments": 30, "shares": 10},
        "full_reset": {"views": 3000, "likes": 10, "comments": 2, "shares": 0},
    }


@pytest.fixture
def sample_analytics():
    """Sample analytics entries."""
    return [
        {
            "post_id": "p1",
            "title": "Test post 1",
            "metrics": {"views": 80000, "likes": 3000, "comments": 500, "shares": 200},
            "diagnosis": {"diagnosis": "SCALE IT", "action": "scale action", "priority": "high"},
        },
        {
            "post_id": "p2",
            "title": "Test post 2",
            "metrics": {"views": 60000, "likes": 500, "comments": 50, "shares": 20},
            "diagnosis": {"diagnosis": "FIX CTA", "action": "fix cta action", "priority": "medium"},
        },
    ]


@pytest.fixture
def sample_hook_analysis():
    """Sample hook analysis result."""
    return {
        "top_hooks": [
            {"hook": "This app changed my life", "views": 80000},
            {"hook": "Stop using bad apps", "views": 50000},
            {"hook": "I found something amazing", "views": 30000},
        ],
        "worst_hooks": [],
        "avg_views": 40000,
        "avg_engagement": 3.5,
        "total_posts": 10,
    }
