"""Compatibility shim for the renamed steel financial summary module.

Use :mod:`steel.steel_financial_summary` for new code.
"""

from steel.steel_financial_summary import *  # noqa: F401,F403
from steel.steel_financial_summary import (
    _WORKFLOW,
    _distribution_stat,
    _project_root,
    _steel_financial_metric_config,
    _with_deterministic_retrofit_mode,
    _with_steel_display_labels,
)


if __name__ == "__main__":
    main()
