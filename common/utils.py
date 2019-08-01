import logging


def setupLogger():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s.%(msecs)03d "
                               "%(levelname)5s: %(message)s",
                        datefmt="%H:%M:%S")


def makeErrorResponse(message=None):
    if message is None:
        return {"result": "ok"}
    return {"result": "error", "message": message}
