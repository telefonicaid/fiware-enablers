__author__ = 'henar'

import ConfigParser
from scripts.getnids.getnid import NID
from scripts.getnids import getnid
import os

class Config():

    CONFIG_COOKBOOK = {}
    CONFIG_PRODUCT = {}
    NID = {}

    def __init__(self, setting_path):
        print "cofnig"
        Config.CONFIG_COOKBOOK = self.load_config(setting_path + '/settings/cookbooks_urls')
        Config.CONFIG_PRODUCT = self.load_config(setting_path + '/settings/product_names')
        Config.NID = self.get_all_nids()
        print os.path.abspath(".")

    def load_config(self, file):
        print "loading config"
        config_product = ConfigParser.RawConfigParser()
        config_product.read(file)
        return config_product

    def get_all_nids(self):
        all_nids = {}
        nid = NID()
        params = {}
        params['--wikitext'] = False

        for chapter in nid.TYPE.keys():
            params['--type'] = chapter
            params[chapter] = True
            nids = getnid.processingnid(params).values()[0]
            all_nids.update(nids)
            params[chapter] = False
        return all_nids