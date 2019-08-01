import asyncio
from functools import wraps
import logging

DEFAULT_TIMEOUT = 30


def shutdown(*procs):
    for p in procs:
        p.kill()

def setupLogger(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(filename, mode="w"))
    return logger

def exception_handler(f):
    @wraps(f)
    async def wrapper():
        loop = asyncio.get_event_loop()

        def ex_hndlr(loop, context):
            print(f"Exception catched from the loop {context}")
            wrapper.error = context["exception"]
            wrapper.task.cancel()
            async def cancel_task(task):
                task.cancel()
                await task
                loop.stop()
            loop.create_task(cancel_task(wrapper.task))
        loop.set_exception_handler(ex_hndlr)
        wrapper.error = None

        async def cancel_timeout(timeout):
            try:
                await asyncio.sleep(timeout)
                wrapper.error = Exception(
                    f"Test is running more than {timeout} seconds")
                print("canceled")
                wrapper.task.cancel()
                await wrapper.task
                loop.stop()
            except BaseException:
                pass
        t = loop.create_task(cancel_timeout(DEFAULT_TIMEOUT))
        wrapper.task = loop.create_task(f())
        res = await wrapper.task
        t.cancel()
        if not wrapper.error:
            return res
        return wrapper.error
    return wrapper
