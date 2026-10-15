"""Rules for decoding and grouping FJC IDB codes.

The rules are divided into modules by case type, and every rule is available
directly from this package (for example, `rules.circuits`).

"""

from __future__ import annotations

from .appellate import *  # noqa: F403
from .civil import *  # noqa: F403
from .courts import *  # noqa: F403
from .criminal import *  # noqa: F403
from .offenses import *  # noqa: F403
