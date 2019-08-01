#!/usr/bin/env python3
import asyncio
from testing import shutdown, setupLogger, exception_handler
from testing.process import AsyncProcess
from termcolor import colored


async def write_lines(stream, lines):
    for l in lines:
        try:
            stream.write(l.encode())
            stream.write(b"\n")
            await stream.drain()
            await asyncio.sleep(0.01)
        except ConnectionResetError:
            print("reset")
            break
        except BaseException:
            print("other")

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
        print(f"{list(names)}")
        r = await asyncio. gather(
            c2.read_until(lambda x: "session found" in x),
            c1.read_until(lambda x: "session found" in x)
        )
        data = ["line " + str(x) for x in range(200)]
        loop.create_task(write_lines(c2.p.stdin, data))
        for l in data:
                r = await c1.read_until(lambda x: l in x)
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
        await c1.read_until(lambda x: "My name" in x),
        await c1.read_until(lambda x: "ws connected" in x),

        async def write_line(stream, line):
            try:
                stream.write(line.encode())
                stream.write(b"\n")
                await stream.drain()
            except ConnectionResetError:
                print("reset")
            except BaseException:
                print("other")
        loop.create_task(write_line(c1.p.stdin, "Hello"))
        await asyncio.sleep(1)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c1)


tests = [run_connect_test, run_single_client_test]
for test in tests:
    try:
        print(colored(f"run {test.__name__}", "yellow"))
        res = loop.run_until_complete(test())
        if res is None:
            print(colored("OK", "green"))
        else:
            print(colored(f"Test failed: {res}", "red"))
    except RuntimeError:
        print("event loop stopped")



