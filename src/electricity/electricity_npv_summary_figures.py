"""Compatibility shim for the renamed electricity financial summary module.

Use :mod:`electricity.electricity_financial_summary` for new code.
"""

from electricity.electricity_financial_summary import *  # noqa: F401,F403
from electricity.electricity_financial_summary import (
    _WORKFLOW,
    _distribution_stat,
    _electricity_financial_metric_config,
    _project_root,
    _with_deterministic_retrofit_mode,
    _with_electricity_display_labels,
)


if __name__ == "__main__":
    main()
