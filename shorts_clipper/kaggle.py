"""Kaggle module entrypoint.

Calls the main kaggle_boot script.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the root of the project is in the Python path to import kaggle_boot
try:
    import kaggle_boot
except ImportError:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    import kaggle_boot

def main() -> None:
    """Run the Kaggle bootstrapper."""
    kaggle_boot.main()

if __name__ == "__main__":
    main()
