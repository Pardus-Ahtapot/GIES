# -*- coding: utf-8 -*-
import subprocess


class Email:

    def __init__(self, receiver_mail):

        self.receiver = receiver_mail

    def send(self, subject, message):

        subprocess.call(["mail -s \"" + subject + "\" " + self.receiver + " < " + message], shell=True)
