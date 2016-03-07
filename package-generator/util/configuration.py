#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#

import ConfigParser
from scripts.getnids.getnid import NID
from scripts.getnids import getnid
from util.utils_clients import util_apis


class Config():

    CONFIG_COOKBOOK = {}
    CONFIG_MODULES = {}
    CONFIG_PRODUCT_NIDS = {}
    CONFIG_PRODUCT_NAMES = {}
    CONFIG_MURANOAPPS = {}
    CONFIG_PACKAGE_NAME = {}

    NID = {}
    Clients = {}

    def __init__(self, auth_url, user, password, tenant_id, region_name):
        """
        Constructor
        :param auth_url: the keystone url
        :param user: the user
        :param password: the password
        :param tenant_id: tenant ID
        :param region_name: the region
        :return: nothing
        """
        Config.CONFIG_COOKBOOK = self.load_config('./settings/cookbooks_urls')
        Config.CONFIG_MODULES = self.load_config('./settings/modules_urls')
        Config.CONFIG_PRODUCT_NIDS = self.load_config('./settings/product_names_for_nids')
        Config.CONFIG_PRODUCT_NAMES = self.load_config('./settings/product_cookbook_names')
        Config.CONFIG_MURANOAPPS = \
            self.load_config('./settings/muranopackages_urls')
        Config.CONFIG_PACKAGE_NAME = self.load_config('./settings/package_names')
        Config.NID = self.get_all_nids()
        Config.Clients = util_apis(auth_url, user, password, tenant_id,
                                   region_name)

    def load_config(self, file):
        """
        It loads the configuration file
        :param file: The configuration file
        :return: nothing
        """
        config_product = ConfigParser.RawConfigParser()
        config_product.read(file)
        return config_product

    def get_all_nids(self):
        """
        It obtains all nids
        :return: Array with nids
        """

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
