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
import unittest
from model.cookbook import Cookbook
import ConfigParser
import mock
from util.configuration import Config
import ConfigParser

COOKBOOK_NAME = "product"
COOKBOOK_URL = "http://product.git"
COOKBOOK_CHILD = "child"
COOKBOOK_CHILD2 = "child2"
COOKBOOK_CHILD_URL = "http://child.git"
COOKBOOK_CHILD_URL2 = "http://child2.git"
PRODUCT_VERSION = "productVersion"
metadata_product_child = "depends \'" + COOKBOOK_CHILD + "\'"
metadata_product_child2 = "depends \'" + COOKBOOK_CHILD2 + "\'"
metadata_product_no_child = "other"


class TestCookbook(unittest.TestCase):

    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    @mock.patch('os.makedirs')
    @mock.patch('util.configuration.Config')
    def setUp(self, mock_conf, mock_path, mock_mkdir, mock_makedir):
        config_product = ConfigParser.RawConfigParser()
        config_product.add_section("main")
        config_product.set("main", COOKBOOK_NAME, COOKBOOK_URL)
        config_product.set("main", COOKBOOK_CHILD, COOKBOOK_CHILD_URL)
        config_product.set("main", COOKBOOK_CHILD2, COOKBOOK_CHILD_URL2)
        Config.CONFIG_COOKBOOK = config_product
        mock_path.return_value = True
        mock_mkdir.return_value = None
        mock_makedir.return_value = None

    def tearDown(self):
        self.mock_open.reset_mock()
        pass

    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_cookbook_no_child(self, mock_open,  mock_exists):
        """test the object is correctly built"""
        mock_exists.return_value = True
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        cookbook = Cookbook(COOKBOOK_NAME)
        self.assertEquals(cookbook.get_cookbook_name(), COOKBOOK_NAME)
        self.assertEquals(len(cookbook.get_cookbooks_child()), 0)
        self.assertEquals(len(cookbook.get_all_cookbooks_child()), 0)
        self.assertEquals(cookbook.get_url(), COOKBOOK_URL)
        self.mock_open.reset_mock()

    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_cookbook_one_child(self, mock_open,  mock_exists):
        """test the object is correctly built"""
        mock_exists.return_value = True
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        cookbook = Cookbook(COOKBOOK_NAME)
        self.assertEquals(cookbook.get_cookbook_name(), COOKBOOK_NAME)
        self.assertEquals(len(cookbook.get_cookbooks_child()), 1)
        self.assertEquals(len(cookbook.get_all_cookbooks_child()), 1)
        self.assertEquals(cookbook.get_url(), COOKBOOK_URL)
        for cookbook_child in cookbook.get_cookbooks_child():
            self.assertEquals(cookbook_child.get_cookbook_name(),
                              COOKBOOK_CHILD)
            self.assertEquals(cookbook_child.get_url(), COOKBOOK_CHILD_URL)
            self.assertEqual(len(cookbook_child.get_cookbooks_child()), 0)
        self.mock_open.reset_mock()

    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_cookbook_one_child_child(self, mock_open, mock_exists):
        """test the object is correctly built"""
        mock_exists.return_value = True
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child2).return_value,
            mock.mock_open(read_data=metadata_product_child2).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        cookbook = Cookbook(COOKBOOK_NAME)
        self.assertEquals(cookbook.get_cookbook_name(), COOKBOOK_NAME)
        self.assertEquals(cookbook.get_url(), COOKBOOK_URL)
        self.assertEquals(len(cookbook.get_cookbooks_child()), 1)
        for cookbook_child in cookbook.get_cookbooks_child():
            self.assertEquals(cookbook_child.get_cookbook_name(),
                              COOKBOOK_CHILD)
            self.assertEquals(cookbook_child.get_url(), COOKBOOK_CHILD_URL)
            self.assertEqual(len(cookbook_child.get_cookbooks_child()), 1)
        self.assertEquals(len(cookbook.get_all_cookbooks_child()), 2)
        self.mock_open.reset_mock()
