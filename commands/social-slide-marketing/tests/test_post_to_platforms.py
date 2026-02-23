"""Tests for post_to_platforms.py — _build_post_payload() and load_config()."""

import json
import pytest
import post_to_platforms as ptp


class TestLoadConfigPostToPlatforms:
    """Test load_config() error handling in post_to_platforms.py."""

    def test_load_valid_config(self, tmp_config):
        config_path, expected = tmp_config
        result = ptp.load_config(config_path)
        assert result["app"]["name"] == "TestApp"

    def test_load_missing_config_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Config not found"):
            ptp.load_config(str(tmp_path / "nonexistent.json"))

    def test_load_invalid_json_raises_value_error(self, tmp_invalid_json):
        with pytest.raises(ValueError, match="Invalid JSON"):
            ptp.load_config(tmp_invalid_json)


class TestBuildPostPayload:
    """Test _build_post_payload() shared extraction."""

    def test_returns_tuple(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        result = ptp._build_post_payload(config, images, "test caption", "test title")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_payload_structure(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, platforms = ptp._build_post_payload(config, images, "caption", "title")
        assert payload["type"] == "now"
        assert "posts" in payload
        assert isinstance(payload["posts"], list)

    def test_default_platforms_from_config(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, platforms = ptp._build_post_payload(config, images, "caption", "title")
        assert "tiktok" in platforms
        assert "instagram" in platforms

    def test_explicit_platforms_override(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, platforms = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["tiktok"]
        )
        assert platforms == ["tiktok"]

    def test_tiktok_post_included(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["tiktok"]
        )
        tiktok_posts = [
            p for p in payload["posts"]
            if p.get("settings", {}).get("__type") == "tiktok"
        ]
        assert len(tiktok_posts) == 1

    def test_tiktok_settings(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["tiktok"]
        )
        tiktok = payload["posts"][0]
        settings = tiktok["settings"]
        assert settings["privacy_level"] == "SELF_ONLY"
        assert settings["video_made_with_ai"] is True
        assert settings["title"] == "title"

    def test_instagram_post_included(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["instagram"]
        )
        ig_posts = [
            p for p in payload["posts"]
            if p.get("settings", {}).get("__type") == "instagram"
        ]
        assert len(ig_posts) == 1

    def test_instagram_caption_has_hashtags(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "my caption", "title", platforms=["instagram"]
        )
        ig_post = payload["posts"][0]
        content = ig_post["value"][0]["content"]
        assert "my caption" in content
        assert "#" in content

    def test_both_platforms(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["tiktok", "instagram"]
        )
        assert len(payload["posts"]) == 2

    def test_no_integration_ids_empty_posts(self):
        config = {
            "postiz": {"integrationIds": {}},
            "posting": {"privacyLevel": "SELF_ONLY", "crossPost": [], "autoAddMusic": True},
        }
        images = [{"id": "img1"}]
        payload, _ = ptp._build_post_payload(
            config, images, "caption", "title", platforms=["tiktok"]
        )
        assert payload["posts"] == []

    def test_does_not_mutate_input_config(self, tmp_config):
        _, config = tmp_config
        original = json.dumps(config, sort_keys=True)
        images = [{"id": "img1"}]
        ptp._build_post_payload(config, images, "caption", "title")
        assert json.dumps(config, sort_keys=True) == original

    def test_does_not_mutate_input_platforms(self, tmp_config):
        _, config = tmp_config
        images = [{"id": "img1"}]
        platforms = ["tiktok"]
        ptp._build_post_payload(config, images, "caption", "title", platforms=platforms)
        assert platforms == ["tiktok"]


class TestBuildInstagramCaption:
    """Test Instagram caption builder."""

    def test_adds_cta(self):
        config = {"app": {"category": "productivity"}}
        result = ptp.build_instagram_caption("test caption", config)
        assert "저장" in result

    def test_adds_hashtags_for_known_category(self):
        config = {"app": {"category": "fitness"}}
        result = ptp.build_instagram_caption("test", config)
        assert "#운동앱" in result

    def test_default_hashtags_for_unknown_category(self):
        config = {"app": {"category": "unknown_cat"}}
        result = ptp.build_instagram_caption("test", config)
        assert "#앱추천" in result

    def test_preserves_original_caption(self):
        config = {"app": {"category": "productivity"}}
        result = ptp.build_instagram_caption("my original text", config)
        assert result.startswith("my original text")
