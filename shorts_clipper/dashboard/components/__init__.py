from __future__ import annotations

from .home import build_home_tab
from .sources import build_sources_tab
from .settings_ui import build_settings_tab
from .providers import build_providers_tab

__all__ = [
    "build_home_tab",
    "build_sources_tab",
    "build_settings_tab",
    "build_providers_tab",
]
