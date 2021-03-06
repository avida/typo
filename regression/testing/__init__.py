import asyncio
from functools import wraps
import logging
import os
import traceback

DEFAULT_TIMEOUT = 300


def shutdown(*procs):
    for p in procs:
        p.kill()


def setupLogger(filename, directory=""):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)
    filename = os.path.join(directory, filename)
    logger.addHandler(logging.FileHandler(filename, mode="w"))
    return logger


def tag(tagname):
    def wrapper(f):
        @wraps(f)
        async def wrapper2(*args, **kvargs):
            res = await f(*args, **kvargs)
            if hasattr(f, "error") and f.error:
                return f.error
            else:
                return res
            return res
        wrapper2.tag = tagname
        return wrapper2
    return wrapper


def maketestdir(base_dir):
    def maketestdir2(f):
        @wraps(f)
        async def wrapper(*args, **kvargs):
            test_dir = os.path.join(base_dir, f.__name__)
            if not os.path.isdir(test_dir):
                os.mkdir(test_dir)
            kvargs["test_dir"] = test_dir
            res = await f(*args, **kvargs)
            if hasattr(f, "error") and f.error:
                return f.error
            else:
                return res
        return wrapper
    return maketestdir2


def exception_handler(f):
    @wraps(f)
    async def wrapper(*args, **kvargs):
        loop = asyncio.get_event_loop()

        def ex_hndlr(loop, context):
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
        res = None
        try:
            res = await wrapper.task
        except asyncio.CancelledError:
            pass
        except BaseException as e:
            res = e
            traceback.print_exc()

        t.cancel()
        if not wrapper.error:
            return res
        return wrapper.error
    return wrapper
