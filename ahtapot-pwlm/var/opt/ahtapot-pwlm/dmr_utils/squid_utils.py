# -*- coding: utf-8 -*-


class WhiteList:

    def __init__(self, file_path):

        self.whitelist = file_path

    def add_to(self, url):

        with open(self.whitelist, "a") as whitelist:
            whitelist.write(url + "\n")

    def check_if_exists(self, url):

        with open(self.whitelist, "r") as whitelist:
            lines = whitelist.readlines()
        for line in lines:
            if url == line:
                return True
        return False
