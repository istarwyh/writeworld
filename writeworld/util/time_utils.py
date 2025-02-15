import time
from typing import Any, Generator


def timed_generator(gen: Generator[Any, None, None], start_time: float) -> Generator[Any, None, None]:
    """Add timing information to generator output"""
    for item in gen:
        elapsed = time.time() - start_time
        if isinstance(item, str) and item.startswith("data:"):
            # For SSE data events, add timing before the newlines
            base = item.rstrip("\n")
            # Remove the closing brace from the JSON
            if base.endswith("}"):
                base = base[:-1]
            yield f'{base}, "elapsed": {elapsed:.3f}}}\n\n'
        else:
            yield item
