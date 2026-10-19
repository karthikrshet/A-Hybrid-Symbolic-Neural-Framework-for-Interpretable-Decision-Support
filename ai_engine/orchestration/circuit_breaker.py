"""Circuit breaker pattern preventing cascade failures across multi-agent dispatches."""

import time
from enum import Enum
from typing import Callable, Any
