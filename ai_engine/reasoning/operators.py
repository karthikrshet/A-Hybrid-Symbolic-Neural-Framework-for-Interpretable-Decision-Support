"""Extended condition evaluation operators for forward-chaining rule engine."""

import re
from typing import Any, List, Set, Union

def op_between(val: float, bounds: List[float]) -> bool:
    """Check if value falls within [min, max] inclusive."""
    return bounds[0] <= val <= bounds[1]

def op_regex(val: str, pattern: str) -> bool:
    """Check if string matches regex pattern."""
    return bool(re.search(pattern, str(val)))
