import asyncio
from functools import wraps
import logging
import os

DEFAULT_TIMEOUT = 30


def shutdown(*procs):
    for p in procs:
        p.kill()


def setupLogger(filename, directory=""):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)
    filename = os.path.join(directory, filename)
    logger.addHandler(logging.FileHandler(filename, mode="w"))
    return logger


def maketestdir(base_dir):
    def maketestdir2(f):
        @wraps(f)
        async def wrapper(*args, **kvargs):
            test_dir = os.path.join(base_dir, f.__name__)
            if not os.path.isdir(test_dir):
                os.mkdir(test_dir)
            kvargs["test_dir"] = test_dir
            await f(*args, **kvargs)
            if hasattr(f, "error"):
                return f.error
        return wrapper
    return maketestdir2


def exception_handler(f):
    @wraps(f)
    async def wrapper(*args, **kvargs):
        loop = asyncio.get_event_loop()

        def ex_hndlr(loop, context):
            # print(f"{context}")
            wrapper.error = context["exception"]
            wrapper.task.cancel()

            async def cancel_task(task):
                task.cancel()
                await task
            loop.create_task(cancel_task(wrapper.task))
        loop.set_exception_handler(ex_hndlr)
        wrapper.error = None

        async def cancel_timeout(timeout):
            try:
                await asyncio.sleep(timeout)
                wrapper.error = Exception(
                    f"Test is running more than {timeout} seconds")
                wrapper.task.cancel()
                await wrapper.task
            except BaseException:
                pass
        t = loop.create_task(cancel_timeout(DEFAULT_TIMEOUT))
        wrapper.task = loop.create_task(f(*args, **kvargs))
        res = await wrapper.task
        t.cancel()
        if not wrapper.error:
            return res
        return wrapper.error
    return wrapper
