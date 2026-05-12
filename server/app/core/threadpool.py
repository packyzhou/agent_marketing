import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable


BLOCKING_THREAD_POOL_SIZE = max(1, (os.cpu_count() or 1) // 4)
blocking_executor = ThreadPoolExecutor(
    max_workers=BLOCKING_THREAD_POOL_SIZE,
    thread_name_prefix="blocking-io",
)


async def run_blocking(func: Callable[..., Any], *args, **kwargs) -> Any:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(blocking_executor, partial(func, *args, **kwargs))
