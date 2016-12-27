# -*- coding: utf8 -*-

from ConfigParser import ConfigParser


class DmrConfigParser:
    def __init__(self):

        self.config = ConfigParser()
        self.config_path = "config.ini"

    def config_section_map(self, section):

        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("Gec  %s" % option)
            except:
                print("Hata : %s!" % option)
                dict1[option] = None
        return dict1

    def get_path_configs(self):

        self.config.read(self.config_path)
        conf = {"squid_repo_path": self.config_section_map("Paths")["squid_repo_path"],
                "whitelist_file": self.config_section_map("Paths")["whitelist_file"],
                "confirm_branch": self.config_section_map("Paths")["confirm_branch"],
                "master_branch": self.config_section_map("Paths")["master_branch"],
                "receiver_mail": self.config_section_map("Paths")["receiver_mail"]}
        return conf

    def config_write(self):
        with open(self.config_path, 'wb') as config_file:
            self.config.write(config_file)
        config_file.close()

    def set_path_configs(self,conf):
        self.config.read(self.config_path)
        for key, value in conf.iteritems():
            self.config.set("Paths", key, value)
        self.config_write()

