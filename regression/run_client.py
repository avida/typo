#!/usr/bin/env python3
import asyncio
from testing import shutdown, setupLogger, exception_handler, async_wait
from testing.process import AsyncProcess


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
def run_connect_test():
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log"))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client1.log"))
        c2 = AsyncProcess("./typo.py", "--config",
                          "test_config/config2",
                          logger=setupLogger("client2.log"))
        loop.run_until_complete(asyncio.gather(
            srv.spawn(), c1.spawn(), c2.spawn()))
        names = loop.run_until_complete(asyncio. gather(
            c1.read_until(lambda x: "My name" in x),
            c2.read_until(lambda x: "My name" in x)
        ))
        names = map(lambda x: x.split()[-1], names)
        print(f"{list(names)}")
        loop.run_until_complete(asyncio. gather(
            c2.read_until(lambda x: "session found" in x),
            c1.read_until(lambda x: "session found" in x)
        ))
        data = ["line " + str(x) for x in range(300)]
        loop.create_task(write_lines(c2.p.stdin, data))
        for l in data:
            loop.run_until_complete(
                c1.read_until(lambda x: l in x)
            )
    except RuntimeError:
        shutdown(srv, c1, c2, timeout=None)
    except BaseException as e:
        return e
    else:
        shutdown(srv, c1, c2, timeout=0)


@exception_handler
def run_single_client_test():
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server_2.log"))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client_1.log"))
        loop.run_until_complete(asyncio.gather(
            srv.spawn(), c1.spawn()))
        loop.run_until_complete(
            c1.read_until(lambda x: "My name" in x),
        )
        loop.run_until_complete(
            c1.read_until(lambda x: "ws connected" in x),
        )

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
        async_wait(1)
    except RuntimeError:
        shutdown(srv, c1, timeout=None)
    else:
        shutdown(srv, c1, timeout=0)


tests = [run_connect_test, run_single_client_test]
for test in tests:
    print(f"running {test.__name__}")
    err = test()
    if err:
        print(
            f"Test {test.__name__} finished with error "
            f"{type(err).__name__}: '{err}'")
    else:
        print(f"Test {test.__name__} finished successfuly")
