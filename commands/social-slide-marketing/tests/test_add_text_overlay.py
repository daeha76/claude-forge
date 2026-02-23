"""Tests for add_text_overlay.py — find_font() caching and text helpers."""

import functools
import pytest
import add_text_overlay as ato


class TestFindFont:
    """Test find_font() with lru_cache."""

    def test_returns_string(self):
        result = ato.find_font()
        assert isinstance(result, str)

    def test_cached_result_is_same(self):
        first = ato.find_font()
        second = ato.find_font()
        assert first == second

    def test_is_lru_cached(self):
        assert hasattr(ato.find_font, "cache_info")
        info = ato.find_font.cache_info()
        assert info.maxsize == 1

    def test_cache_hit_after_first_call(self):
        ato.find_font.cache_clear()
        ato.find_font()
        info_after_first = ato.find_font.cache_info()
        ato.find_font()
        info_after_second = ato.find_font.cache_info()
        assert info_after_second.hits == info_after_first.hits + 1


class TestWrapText:
    """Test wrap_text() text wrapping logic."""

    def _get_font(self):
        from PIL import ImageFont
        font_path = ato.find_font()
        if font_path:
            try:
                return ImageFont.truetype(font_path, 40)
            except Exception:
                pass
        return ImageFont.load_default()

    def test_short_text_single_line(self):
        font = self._get_font()
        lines = ato.wrap_text("Hello", font, 1000)
        assert len(lines) == 1
        assert lines[0] == "Hello"

    def test_max_three_lines(self):
        font = self._get_font()
        long_text = " ".join(["word"] * 50)
        lines = ato.wrap_text(long_text, font, 200)
        assert len(lines) <= 3

    def test_manual_line_breaks(self):
        font = self._get_font()
        lines = ato.wrap_text("Line1\\nLine2\\nLine3", font, 1000)
        assert lines == ["Line1", "Line2", "Line3"]

    def test_empty_text(self):
        font = self._get_font()
        lines = ato.wrap_text("", font, 1000)
        assert lines == []


class TestProcessSlides:
    """Test process_slides() with real temp files."""

    def test_nonexistent_directory_returns_empty(self):
        result = ato.process_slides("/nonexistent/path", "text1||text2")
        assert result == []

    def test_empty_directory_returns_empty(self, tmp_path):
        result = ato.process_slides(str(tmp_path), "text1||text2")
        assert result == []

    def test_copy_when_no_text(self, tmp_path):
        from PIL import Image
        slide = tmp_path / "slide_01.png"
        img = Image.new("RGB", (100, 100), "white")
        img.save(str(slide))

        result = ato.process_slides(str(tmp_path), "")
        assert len(result) == 1
        assert "final" in result[0]

    def test_text_overlay_applied(self, tmp_path):
        from pathlib import Path as P
        from PIL import Image
        slide = tmp_path / "slide_01.png"
        img = Image.new("RGB", (1080, 1920), "blue")
        img.save(str(slide))

        output_dir = str(tmp_path / "out")
        result = ato.process_slides(str(tmp_path), "Hello World", output_dir=output_dir)
        assert len(result) == 1
        assert P(result[0]).exists()

    def test_multiple_slides(self, tmp_path):
        from PIL import Image
        for i in range(3):
            slide = tmp_path / f"slide_{i:02d}.png"
            img = Image.new("RGB", (200, 200), "red")
            img.save(str(slide))

        result = ato.process_slides(
            str(tmp_path), "Text1||Text2||Text3", output_dir=str(tmp_path / "out")
        )
        assert len(result) == 3


class TestAddTextOverlay:
    """Test add_text_overlay() single image processing."""

    def test_success_returns_true(self, tmp_path):
        from PIL import Image
        src = tmp_path / "source.png"
        img = Image.new("RGB", (500, 500), "green")
        img.save(str(src))

        out = tmp_path / "output.png"
        result = ato.add_text_overlay(str(src), "Test", str(out))
        assert result is True
        assert out.exists()

    def test_nonexistent_image_returns_false(self, tmp_path):
        result = ato.add_text_overlay("/nonexistent.png", "Test", str(tmp_path / "out.png"))
        assert result is False

    def test_empty_text_returns_false(self, tmp_path):
        from PIL import Image
        src = tmp_path / "source.png"
        img = Image.new("RGB", (500, 500), "green")
        img.save(str(src))

        result = ato.add_text_overlay(str(src), "", str(tmp_path / "out.png"))
        assert result is False
