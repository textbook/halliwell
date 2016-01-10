import asyncio

import pytest


def future_from(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)
