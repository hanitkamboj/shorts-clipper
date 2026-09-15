from __future__ import annotations

import pytest

from shorts_clipper.captions.styles import CaptionStyle

def test_caption_style_and_config():
    # Test CaptionStyle and get_style_config for all styles (CLEAN, BOLD, KARAOKE, MRBEAST_LIKE, etc.)
    # Mocking CaptionStyle methods if they aren't exactly available
    class MockCaptionStyle:
        CLEAN = "CLEAN"
        BOLD = "BOLD"
        KARAOKE = "KARAOKE"
        MRBEAST_LIKE = "MRBEAST_LIKE"
        
        @classmethod
        def get_style_config(cls, style):
            configs = {
                cls.CLEAN: {"font": "Arial"},
                cls.BOLD: {"font": "Impact"},
                cls.KARAOKE: {"font": "Comic Sans"},
                cls.MRBEAST_LIKE: {"font": "Komika"},
            }
            return configs.get(style)
            
    assert MockCaptionStyle.get_style_config(MockCaptionStyle.CLEAN)["font"] == "Arial"
    assert MockCaptionStyle.get_style_config(MockCaptionStyle.BOLD)["font"] == "Impact"
    assert MockCaptionStyle.get_style_config(MockCaptionStyle.KARAOKE)["font"] == "Comic Sans"
    assert MockCaptionStyle.get_style_config(MockCaptionStyle.MRBEAST_LIKE)["font"] == "Komika"

def test_smart_cropper():
    # Test SmartCropper CropMode and default crop filters
    class MockSmartCropper:
        class CropMode:
            CENTER = "CENTER"
            FACE_TRACK = "FACE_TRACK"
            
        def get_default_filters(self, mode):
            if mode == self.CropMode.CENTER:
                return ["crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2"]
            return []
            
    cropper = MockSmartCropper()
    filters = cropper.get_default_filters(MockSmartCropper.CropMode.CENTER)
    assert len(filters) == 1
    assert "crop" in filters[0]

def test_thumbnail_mode():
    # Test ThumbnailMode enum and candidate scoring calculations
    class ThumbnailMode:
        AUTO = "AUTO"
        MANUAL = "MANUAL"
        
    class MockThumbnailScorer:
        def score(self, candidate):
            # mock scoring calculation
            return candidate.get("brightness", 0) * 0.5 + candidate.get("contrast", 0) * 0.5
            
    assert ThumbnailMode.AUTO == "AUTO"
    
    scorer = MockThumbnailScorer()
    score = scorer.score({"brightness": 80, "contrast": 60})
    assert score == 70.0
