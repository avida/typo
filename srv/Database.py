#!/usr/bin/env python3
import json
import os


class Database:

    def storeUserInfo(self, userId, userInfo):
        raise NotImplementedError()

    def getUserInfo(self, userId):
        raise NotImplementedError()


class JsonDatabase(Database):
    def __init__(self, filename):
        self.users = {}
        self.filename = filename

    def storeUserInfo(self, userId, userInfo):
        self.users[userId] = userInfo
        self.save()

    def getUserInfo(self, userId):
        if userId not in self.users:
            return None
        return self.users[userId]

    def save(self):
        with open(self.filename, "w") as file:
            data = json.dumps(self.users)
            file.write(data)

    def load(self):
        try:
            with open(self.filename, "r") as file:
                data = file.read()
                self.users = json.loads(data)
        except FileNotFoundError:
            self.users = {}

    @staticmethod
    def cleanup(filename):
        if os.path.isfile(filename):
            os.remove(filename)
