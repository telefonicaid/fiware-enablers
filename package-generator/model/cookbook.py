#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
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

from util import utils
import os
import ConfigParser
from util.configuration import Config
URL_FORGE = "https://forge.fiware.org/scmrepos/svn/testbed/trunk/" \
            "cookbooks/GESoftware/"
KEY_CHILD_PRODUCT = "depends"


class Cookbook:
    """This class represents the cookbook object.
    """
    def __init__(self, name, enabler=False):
        """
        The constructor
        :param name: cookbook name
        :param cookbook_config:  configuration file for cookbook
        :param enabler: is a FIWARE enabler or not
        :return:
        """
        self.name = name
        self.enabler = enabler
        self.url = self._get_url()
        self.cookbook_childs = self._get_cookbook_children_from_metadata()

    def get_cookbook_name(self):
        """
        It returns the cookbook name.
        :return: name
        """
        return self.name

    def get_url(self):
        """It returns the cookbook url
        :return: url
        """
        return self.url

    def get_cookbooks_child(self):
        """
        It returns the children cookbooks.
        :return:
        """
        return self.cookbook_childs

    def _get_url(self):
        """
        It obtains the url for the cookbook. If it is an enabler, the url
        will be the forge, and in case it is not, the url will be found
        in the configuration file
        :return: cookbook url
        """
        url = ''
        if self.enabler:
            url = URL_FORGE + self.name
        else:
            url = Config.CONFIG_COOKBOOK.get("main", self.name)

        return url

    def _get_cookbook_children_from_metadata(self):
        """
        It obtains the children cookbooks from the metadata file
        :return: an Cookbook array with the cookbooks children
        """
        cookbooks = []
        if self._has_child_cookbooks_metadata():
            cookbooks_str = self._get_cookbooks_metadata()
            for cookbook_str in cookbooks_str:
                cookbook = Cookbook(cookbook_str)
                cookbooks.append(cookbook)
        return cookbooks

    def _has_child_cookbooks_metadata(self):
        """
        It checks if the cookbooks has cookbook children checking
        the metadata file
        :return: True/False
        """
        metadata_str = utils.read_metadata(self.url)
        if KEY_CHILD_PRODUCT in metadata_str:
            return True
        return False

    def _get_cookbooks_metadata(self):
        """
        It obtains a cookbook string array from the metadata file
        :return: A string array with the cookbook children
        """
        metadata_str = utils.read_metadata(self.url)
        cookbooks = []
        lines = metadata_str.splitlines()
        for line in lines:
            if KEY_CHILD_PRODUCT in line:
                dep = line.find(KEY_CHILD_PRODUCT)
                if line.find("\'", dep) != -1:
                    beg = line.find("\'")
                    end = line.find("\'", beg + 1)
                else:
                    beg = line.find("\"", dep)
                    end = line.find("\"", beg + 1)
                cookbooks.append(line[beg + 1: end])
        return cookbooks

    def get_all_cookbooks_child(self):
        """
        It obtains a Cookbook array with all cookbooks, the cookbook
        itself plus all cookbooks of their cookbook children and
        recursively.
        :return: Cookbook array
        """
        cookbooks = []
        for cookbook_child in self.cookbook_childs:
            cookbooks.append(cookbook_child)
            if len(cookbook_child.get_cookbooks_child()) != 0:
                cookbooks_in = cookbook_child.get_all_cookbooks_child()
                cookbooks.extend(x for x in cookbooks_in if not self._exists(x.name, cookbooks))
        return cookbooks

    def _exists(self, cookbook_name, cookbooks):
        for cookbook in cookbooks:
            if cookbook_name in cookbook.name:
                return True
        return False
