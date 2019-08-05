#!/usr/bin/env python3
import asyncio
from testing import (shutdown, setupLogger,
                     exception_handler, maketestdir,
                     tag)
from testing.process import AsyncProcess
from termcolor import colored
import os
import argparse

loop = asyncio.get_event_loop()

TEST_DIR = "test_dir"


@maketestdir(TEST_DIR)
@exception_handler
async def run_connect_test(test_dir):
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log", test_dir))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client1.log", test_dir))
        c2 = AsyncProcess("./typo.py", "--config",
                          "test_config/config2",
                          logger=setupLogger("client2.log", test_dir))
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


@maketestdir(TEST_DIR)
@exception_handler
async def run_single_client_test(test_dir):
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log", test_dir))
        c = AsyncProcess("./typo.py", "--config",
                         "test_config/config",
                         logger=setupLogger("client.log", test_dir))
        await asyncio.gather(
            srv.spawn(), c.spawn())

        await srv.read_until(lambda x: "user found" in x),
        await c.read_until(lambda x: "My name" in x),
        await c.read_until(lambda x: "ws connected" in x),

        c.setFailCondition(lambda line: "connection closed" in line)
        srv.setFailCondition(lambda line: "ERROR:" in line)
        c.write_lines("Hello")
        await asyncio.sleep(1)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c)


@exception_handler
@tag("test")
@maketestdir(TEST_DIR)
async def run_clinet_disconnected(test_dir):
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log", test_dir))
        c1 = AsyncProcess("./typo.py", "--config",
                          "test_config/config",
                          logger=setupLogger("client1.log", test_dir))
        c2 = AsyncProcess("./typo.py", "--config",
                          "test_config/config2",
                          logger=setupLogger("client2.log", test_dir))
        await srv.spawn()
        await asyncio.gather(c1.spawn(), c2.spawn())
        srv.setFailCondition(lambda line: "ERROR:" in line)
        await asyncio.gather(
            c1.read_until(lambda x: "ws connected" in x),
            c2.read_until(lambda x: "ws connected" in x)
        )
        c2.kill()
        await asyncio.sleep(1)
        await srv.read_until(lambda x: "disconnected" in x)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, c1, c2)


@exception_handler
@maketestdir(TEST_DIR)
async def run_a_lot_of_clients(test_dir):
    try:
        srv = AsyncProcess("./typo_server.py",
                           logger=setupLogger("server.log", test_dir))
        clients = []
        for c in range(10):
            conf_dir = os.path.join(test_dir, f"config{c}")
            client_process = AsyncProcess("./typo.py", "--config",
                                          conf_dir,
                                          logger=setupLogger(f"client{c}.log",
                                                             test_dir))
            clients.append(client_process)
        await srv.spawn()
        await asyncio.gather(*[c.spawn() for c in clients])
        names = await asyncio.gather(
            *[c.read_until(lambda x: "My name" in x) for c in clients])
        names = [x.split()[-1] for x in names]
        print(names)
    except BaseException as e:
        return e
    finally:
        shutdown(srv, *clients)

tests = [
    run_connect_test,
    run_single_client_test,
    run_clinet_disconnected,
    run_a_lot_of_clients
]

if not os.path.isdir(TEST_DIR):
    os.mkdir(TEST_DIR)


def parseArgs():
    parser = argparse.ArgumentParser(description="run tests")
    parser.add_argument("--tag", type=str, metavar="tags",
                        action="append", default=None)
    return parser.parse_args()


args = parseArgs()

for test in tests:
    try:
        if args.tag is not None:
            if not hasattr(test, "tag") or test.tag not in args.tag:
                print(colored(f"Skipping {test.__name__}", "yellow"))
                continue
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
