import asyncio


def future_from(result):
    future = asyncio.Future()
    future.set_result(result)
    return future
