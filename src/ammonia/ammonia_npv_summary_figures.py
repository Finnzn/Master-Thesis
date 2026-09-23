"""Compatibility shim for the renamed ammonia financial summary module.

Use :mod:`ammonia.ammonia_financial_summary` for new code.
"""

from ammonia.ammonia_financial_summary import *  # noqa: F401,F403
from ammonia.ammonia_financial_summary import (
    _WORKFLOW,
    _ammonia_financial_metric_config,
    _distribution_stat,
    _project_root,
    _with_ammonia_display_labels,
    _with_deterministic_retrofit_mode,
)


if __name__ == "__main__":
    main()
