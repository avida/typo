#!/usr/bin/env python3
import logging 

class Database:
    def __init__(self):
        logging.warn("init")

    def storeUserInfo(self, userId):
        logging.warn("store")

    def getUserInfo(self, userId):
        return {}

if __name__ == "__main__":
    import fire
    fire.Fire(Database)
