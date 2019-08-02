#!/usr/bin/env python3
import asyncio
from testing import shutdown, setupLogger, exception_handler
from testing.process import AsyncProcess
from termcolor import colored

loop = asyncio.get_event_loop()


@exception_handler
async def run_connect_test():
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log"))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client1.log"))
        c2 = AsyncProcess("./typo.py", "--config",
                          "test_config/config2",
                          logger=setupLogger("client2.log"))
        await asyncio.gather(
            srv.spawn(), c1.spawn(), c2.spawn())

        names = await asyncio. gather(
            c1.read_until(lambda x: "My name" in x),
            c2.read_until(lambda x: "My name" in x)
        )

        names = map(lambda x: x.split()[-1], names)
        await asyncio. gather(
            c2.read_until(lambda x: "session found" in x),
            c1.read_until(lambda x: "session found" in x)
        )
        data = ["line " + str(x) for x in range(200)]
        c2.write_lines(data, delay=0.01)
        for l in data:
            await c1.read_until(lambda x: l in x)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c1, c2)


@exception_handler
async def run_single_client_test():
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server_2.log"))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client_1.log"))
        await asyncio.gather(
            srv.spawn(), c1.spawn())

        await srv.read_until(lambda x: "user found" in x),
        await c1.read_until(lambda x: "My name" in x),
        await c1.read_until(lambda x: "ws connected" in x),

        c1.setFailCondition(lambda line: "connection closed" in line)
        srv.setFailCondition(lambda line: "ERROR:" in line)
        c1.write_line("Hello")
        await asyncio.sleep(1)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c1)


@exception_handler
async def run_clinet_disconnected():
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log"))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client1.log"))
        c2 = AsyncProcess("./typo.py", "--config",
                          "test_config/config2",
                          logger=setupLogger("client2.log"))
        await asyncio.gather(
            srv.spawn(), c1.spawn(), c2.spawn())
        await asyncio.gather(
            c1.read_until(lambda x: "ws connected" in x),
            c2.read_until(lambda x: "ws connected" in x)
        )
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c1, c2)


tests = [
    run_connect_test,
    run_single_client_test,
    run_clinet_disconnected,
]
for test in tests:
    try:
        print(colored(f"run {test.__name__}", "yellow"))
        res = loop.run_until_complete(test())
        if res is None:
            print(colored("OK", "green"))
        else:
            print(colored(f"Test failed - {type(res).__name__}: {res}", "red"))
        for t in asyncio.Task.all_tasks():
            t.cancel()
    except RuntimeError:
        print("event loop stopped")
