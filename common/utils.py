import logging


def setupLogger():
    logging.basicConfig(level=logging.DEBUG)


def makeErrorResponse(message=None):
    if message is None:
        return {"result": "ok"}
    return {"result": "error", "message": message}
