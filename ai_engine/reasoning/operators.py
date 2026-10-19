"""Extended condition evaluation operators for forward-chaining rule engine."""

import re
from typing import Any, List, Set, Union

def op_between(val: float, bounds: List[float]) -> bool:
    """Check if value falls within [min, max] inclusive."""
    return bounds[0] <= val <= bounds[1]

def op_regex(val: str, pattern: str) -> bool:
    """Check if string matches regex pattern."""
    return bool(re.search(pattern, str(val)))

def op_set_contains(container: Union[List, Set], item: Any) -> bool:
    """Check set membership."""
    return item in container

def op_subset(subset: List, superset: List) -> bool:
    """Check if collection is subset of target."""
    return set(subset).issubset(set(superset))
