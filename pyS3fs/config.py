# -*- coding: utf-8 -*-

import ConfigParser
import os
import logging 

CONFIG_PATH = os.path.expanduser("~/.pyS3fs/config")


class ConfigFileNotFoundException(Exception):
    pass


class ConfigDirectiveNotFoundException(Exception):
    pass


class _Config(object):
    def __init__(self):
        self.ConfigParser = ConfigParser.ConfigParser()

        try:
            self.ConfigParser.readfp(open(CONFIG_PATH))
        except IOError:
            logging.error("Configuration file was not found on {}. Aborting.".format(
                CONFIG_PATH))
            raise ConfigFileNotFoundException

    def __getitem__(self, name):
        try:
            return self.ConfigParser.get("global", name)
        except ConfigParser.NoOptionError:
            logging.error("Directive {} was not found on {}".format(
                name, CONFIG_PATH))
            raise ConfigDirectiveNotFoundException

config = _Config()


    
