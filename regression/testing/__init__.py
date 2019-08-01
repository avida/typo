import asyncio
from functools import wraps
import logging

DEFAULT_TIMEOUT = 30


def shutdown(*procs, timeout=0):
    loop = asyncio.get_event_loop()
    if timeout is None:
        for p in procs:
            p.p.kill()
    else:
        tasks = [x.kill(timeout) for x in procs]
        loop.run_until_complete(asyncio.gather(*tasks))


def setupLogger(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(filename, mode="w"))
    return logger


def async_wait(timeout):
    async def wait(timeout):
        await asyncio.sleep(timeout)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait(timeout))


def exception_handler(f):
    @wraps(f)
    def wrapper():
        loop = asyncio.get_event_loop()

        def ex_hndlr(loop, context):
            print(f"{context}")
            wrapper.error = context["exception"]
            loop.stop()
        loop.set_exception_handler(ex_hndlr)
        wrapper.error = None

        async def cancel_timeout(timeout):
            try:
                await asyncio.sleep(timeout)
                wrapper.error = Exception(
                    f"Test is running more than {timeout} seconds")
                loop.stop()
            except BaseException:
                pass
        t = loop.create_task(cancel_timeout(DEFAULT_TIMEOUT))
        res = f()
        t.cancel()
        if not wrapper.error:
            return res
        return wrapper.error
    return wrapper
