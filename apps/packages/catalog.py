from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from jx import Catalog

UI_DIR = Path(__file__).resolve().parent
UI_COMPONENTS_DIR = UI_DIR / "components"
UI_STATIC_DIR = UI_DIR / "static"


def build_catalog(*, app_components_dir: Path | None = None, debug: bool = False, **globals: Any) -> Catalog:
    """Build the UI catalog.

    :param app_components_dir: The path to the application's components
        directory.
    :param debug: Enable debug mode, which may include additional
        logging or unminified assets.
    :param globals: Additional global variables to pass to the catalog.

    :return: An instance of :class:`jx.Catalog`
    """
    globals.setdefault("current_year", datetime.now().year)

    catalog = Catalog(auto_reload=debug, **globals)
    catalog.add_folder(str(UI_COMPONENTS_DIR), prefix="ui", preload=True)
    if app_components_dir:
        catalog.add_folder(str(app_components_dir), preload=True)

    return catalog
