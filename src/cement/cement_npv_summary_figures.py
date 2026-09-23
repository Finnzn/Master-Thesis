"""Compatibility shim for the renamed cement financial summary module.

Use :mod:`cement.cement_financial_summary` for new code.
"""

from cement.cement_financial_summary import *  # noqa: F401,F403
from cement.cement_financial_summary import (
    _WORKFLOW,
    _cement_financial_metric_config,
    _distribution_stat,
    _project_root,
    _with_cement_display_labels,
    _with_deterministic_retrofit_mode,
)


if __name__ == "__main__":
    main()
