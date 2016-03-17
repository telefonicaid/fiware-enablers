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
# http://www.apache.org/licenses/LICENSE-2.0
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
from util import utils_file as utils
from util.configuration import Config
import json

URL_FORGE = "https://forge.fiware.org/scmrepos/svn/testbed/trunk/" \
            "cookbooks/GESoftware/"
KEY_CHILD_CHEF = "depends"
KEY_CHILD_PUPPET = "dependencies"
CHEF = "Chef"
PUPPET = "Puppet"
METADATA_RB = "metadata.rb"
METADATA_JSON = "metadata.json"
BERKSFILE = "Berksfile"


class Cookbook:
    """This class represents the cookbook object.
    """

    def __init__(self, name, installator, enabler=False):
        """
        The constructor
        :param name:  cookbook name
        :param installator:  cookbook installator
        :param enabler: is a FIWARE enabler
        :return: nothing
        """
        self.name = self.get_cookbook_name(name)
        self.enabler = enabler
        self.installator = installator
        self.url = self._get_url()
        self.is_berksfile = self.is_berksfile()
        self.cookbook_childs = self._get_cookbook_children_from_metadata()

    def _get_url(self):
        """
        It obtains the url for the cookbook. If it is an enabler, the url
        will be the forge, and in case it is not, the url will be found
        in the configuration file
        :return: cookbook url
        """
        url = self._get_cookbook_url_config()

        if not url:
            if self.enabler:
                url = URL_FORGE + self.name
            else:
                print "No found url for " + self.name

        return url

    def _get_cookbook_url_config(self):
        url = None
        try:
            if self.installator == CHEF:
                url = Config.CONFIG_COOKBOOK.get("main", self.name)
            else:
                url = Config.CONFIG_MODULES.get("main", self.name)
        except Exception as e:
            pass
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
                cookbook = Cookbook(cookbook_str, self.installator)
                cookbooks.append(cookbook)
        return cookbooks

    def _has_child_cookbooks_metadata(self):
        """
        It checks if the cookbooks has cookbook children checking
        the metadata file
        :return: True/False
        """
        if self.url:
            metadata_rb = utils.read_metadata(self.url, METADATA_RB)
            metadata_json = utils.read_metadata(self.url, METADATA_JSON)
            if metadata_rb and KEY_CHILD_CHEF in metadata_rb:
                return True
            elif metadata_json and KEY_CHILD_PUPPET in metadata_json:
                return True
        return False

    def _get_cookbooks_metadata(self):
        """
        It obtains a cookbook string array from the metadata file
        :return: A string array with the cookbook children
        """
        cookbooks = []

        metadata_str_rb = utils.read_metadata(self.url, METADATA_RB)
        metadata_str_json = utils.read_metadata(self.url, METADATA_JSON)

        if metadata_str_rb:
            cookbooks = self._get_cookbooks_metadata_rb(metadata_str_rb)
        if metadata_str_json:
            cookbooks = (cookbooks +
                         self._get_cookbooks_metadata_json(metadata_str_json))
        return cookbooks

    def _get_cookbooks_metadata_rb(self, metadata_str):
        """
        If obtains the cookbooks from the metadata.rb
        :param metadata_str: the metadata rb in string
        :return: cookbook array
        """
        cookbooks = []
        lines = metadata_str.splitlines()
        for line in lines:
            if KEY_CHILD_CHEF in line:
                dep = line.find(KEY_CHILD_CHEF)
                if line.find("\'", dep) != -1:
                    beg = line.find("\'")
                    end = line.find("\'", beg + 1)
                else:
                    beg = line.find("\"", dep)
                    end = line.find("\"", beg + 1)
                cookbooks.append(line[beg + 1: end])
        return cookbooks

    def _get_cookbooks_metadata_json(self, metadata_str):
        """
        If obtains the cookbooks from the metadata.json
        :param metadata_str: the metadata json in string
        :return: cookbook array
        """
        cookbooks = []
        try:
            metadata = json.loads(metadata_str)
        except:
            return cookbooks
        dependences = metadata.get(KEY_CHILD_PUPPET)
        if dependences:
            for dependence in dependences:
                try:
                    de = dependence["name"]
                except:
                    de = dependence
                cookbooks.append(utils.get_name_folder(de))
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
            if not self._exists(cookbook_child.name, cookbooks):
                cookbooks.append(cookbook_child)
            if len(cookbook_child.cookbook_childs) != 0:
                cookbooks_in = cookbook_child.get_all_cookbooks_child()
                cookbooks.extend(x for x in cookbooks_in
                                 if not self._exists(x.name, cookbooks))
        return cookbooks

    def _exists(self, cookbook_name, cookbooks):
        """
        It checks if the cookbooks is in the array
        :param cookbook_name: cookbook name
        :param cookbooks: Cookbooks array
        :return: True/False
        """
        for cookbook in cookbooks:
            if cookbook_name == cookbook.name:
                return True
        return False

    def get_cookbook_name(self, name):
        """
        It obtains the cookbook name in case required.
        :param name:  cookbook name
        :return: cookbook name changed
        """
        try:
            return Config.CONFIG_PRODUCT_NAMES.get('main', name)
        except:
            return name

    def is_berksfile(self):
        """
        It checks if the cookbooks can be installed by berkshell.
        Just trying to find the file Berksfile
        :return: True/False
        """
        berksfile = utils.read_metadata(self.url, BERKSFILE)
        if berksfile and "404" in berksfile:
            return False
        if berksfile and ("source" in berksfile or "site" in berksfile):
            return True
        return False

