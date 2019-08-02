import asyncio


class UnexpectedExit(Exception):
    def __init__(self, p):
        msg = f"{p.p.pid} {' '.join(p.cmd)} exited prematurely"
        Exception.__init__(self, msg)


class UnexpectedLine(Exception):
    def __init__(self, line):
        Exception.__init__(self, line)


class AsyncProcess:
    def __init__(self, *cmd, logger):
        self.cmd = cmd
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self.__on_line = None
        self.killed = False
        self.failCond = None

    def kill(self):
        self.killed = True
        self.p.kill()

    def setFailCondition(self, failCond):
        self.failCond = failCond

    async def spawn(self):
        p = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        self.p = p
        self.loop.create_task(self._listen_output())

    def write_lines(self, lines, delay=0):
        async def _write_lines(stream, lines, delay):
            try:
                for line in lines:
                    stream.write(line.encode())
                    stream.write(b'\n')
                    await stream.drain()
                    if delay != 0:
                        await asyncio.sleep(delay)
            except BaseException:
                pass
        if isinstance(lines, str):
            lines = [lines]
        self.loop.create_task(_write_lines(
            self.p.stdin,
            lines,
            delay))

    async def read_until(self, cond):
        future = asyncio.Future()

        def set_future(line):
            if cond(line):
                future.set_result(line)
        self.__on_line = set_future
        asyncio.ensure_future(future)
        res = await future
        self.__on_line = None
        return res

    async def _listen_output(self):
        while True:
            line = await self.p.stderr.readline()
            line = line.decode().strip()
            if not line:
                if not self.killed:
                    raise UnexpectedExit(self)
                break
            self.logger.info(f"{line}")
            if self.failCond and self.failCond(line):
                raise UnexpectedLine(line)
            if self.__on_line is not None:
                self.__on_line(line)
