"""Compatibility shim for the renamed hydrogen financial summary module.

Use :mod:`hydrogen.hydrogen_financial_summary` for new code.
"""

from hydrogen.hydrogen_financial_summary import *  # noqa: F401,F403
from hydrogen.hydrogen_financial_summary import (
    _WORKFLOW,
    _distribution_stat,
    _hydrogen_financial_metric_config,
    _project_root,
    _with_deterministic_retrofit_mode,
    _with_hydrogen_display_labels,
)


if __name__ == "__main__":
    main()
