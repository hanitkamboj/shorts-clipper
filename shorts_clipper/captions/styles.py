from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class CaptionStyle(StrEnum):
    CLEAN = 'clean'
    BOLD = 'bold'
    KARAOKE = 'karaoke'
    MRBEAST_LIKE = 'mrbeast_like'
    PODCAST = 'podcast'
    MINIMAL = 'minimal'
    CUSTOM = 'custom'

@dataclass(frozen=True)
class CaptionConfig:
    style: CaptionStyle
    font_name: str = 'Arial'
    font_size: int = 48
    primary_color: str = '&H00FFFFFF'  # ASS color format (AABBGGRR)
    highlight_color: str = '&H0000FFFF'  # Yellow highlight
    outline_color: str = '&H00000000'  # Black outline
    shadow_color: str = '&H80000000'
    outline_width: float = 2.0
    shadow_depth: float = 1.0
    bold: bool = False
    italic: bool = False
    uppercase: bool = False
    alignment: int = 2  # ASS alignment (2 = bottom center)
    margin_v: int = 80  # Vertical margin from bottom
    margin_h: int = 40
    max_words_per_line: int = 4
    max_chars_per_line: int = 30
    word_highlight: bool = False  # Highlight current word
    animation: str = 'none'  # 'none', 'fade', 'pop', 'slide'
    words_per_group: int = 3  # Words to show at once

def get_style_config(style: CaptionStyle) -> CaptionConfig:
    """Get the default configuration for a caption style."""
    if style == CaptionStyle.CLEAN:
        return CaptionConfig(
            style=style,
            font_name='Arial',
            font_size=40,
            primary_color='&H00FFFFFF',
            outline_color='&H00000000',
            outline_width=1.0,
            alignment=2,
            word_highlight=False
        )
    elif style == CaptionStyle.BOLD:
        return CaptionConfig(
            style=style,
            font_name='Impact',
            font_size=60,
            primary_color='&H00FFFFFF',
            highlight_color='&H0000FFFF',
            outline_color='&H00000000',
            outline_width=4.0,
            bold=True,
            alignment=5,  # Center
            word_highlight=True
        )
    elif style == CaptionStyle.KARAOKE:
        return CaptionConfig(
            style=style,
            font_name='Arial',
            font_size=50,
            primary_color='&H00FFFFFF',
            highlight_color='&H0000FFFF',
            word_highlight=True,
            animation='none',
            words_per_group=4
        )
    elif style == CaptionStyle.MRBEAST_LIKE:
        return CaptionConfig(
            style=style,
            font_name='Komika Axis',
            font_size=70,
            primary_color='&H00FFFFFF',
            highlight_color='&H0000FFFF',
            outline_color='&H00000000',
            outline_width=5.0,
            shadow_depth=3.0,
            bold=True,
            uppercase=True,
            alignment=5,  # Center
            word_highlight=True,
            animation='pop',
            words_per_group=2
        )
    elif style == CaptionStyle.PODCAST:
        return CaptionConfig(
            style=style,
            font_name='Georgia',
            font_size=36,
            primary_color='&H00FFFFFF',
            outline_color='&H00000000',
            outline_width=1.5,
            alignment=1,  # Bottom left
            margin_h=20,
            margin_v=40,
            word_highlight=False
        )
    elif style == CaptionStyle.MINIMAL:
        return CaptionConfig(
            style=style,
            font_name='Arial',
            font_size=28,
            primary_color='&H00FFFFFF',
            outline_color='&H00000000',
            outline_width=1.0,
            shadow_depth=0.0,
            alignment=2,
            margin_v=20,
            word_highlight=False
        )
    else:
        # CUSTOM or fallback
        return CaptionConfig(style=style)
