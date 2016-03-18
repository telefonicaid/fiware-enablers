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
import unittest
from model.product_package import ProductPackage
from model.product import Product
from util.configuration import Config
import mock
import ConfigParser


COOKBOOK_NAME = "product"
COOKBOOK_URL = "http://product.git"
COOKBOOK_CHILD1 = "child"
COOKBOOK_CHILD2 = "child2"
COOKBOOK_CHILD_URL1 = "http://child1.git"
COOKBOOK_CHILD_URL2 = "http://child2.git"
PRODUCT_VERSION = "productVersion"
metadata_product_child = "depends \'" + COOKBOOK_CHILD1 + "\'"
metadata_product_child2 = "depends \'" + COOKBOOK_CHILD2 + "\'"
metadata_product_no_child = "other"
PRODUCT_NAME = "product"
PRODUCT_MURANO_NAME = "productMurano"

METADATA_JSON = {
    "name": "product",
    "dependencies": [
        {"name": COOKBOOK_CHILD1},
        {"name": COOKBOOK_CHILD2}]}

METADATA_JSON_STR_NO_CHILD = "{ \"name\": \"child\" }"
METADATA_JSON_STR = "{ \"name\": \"product\",  \"dependencies\": " \
                    " [  {\"name\": " + COOKBOOK_CHILD1 + "}," \
                    "  {\"name\": " + COOKBOOK_CHILD2 + "} ] }"
MANIFEST = "{\"Classes\": {\"ID\": \"Myclass\"}}"


class TestProductPackage(unittest.TestCase):
    """Class to test basic operations for the Product class"""
    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    @mock.patch('os.makedirs')
    def setUp(self, mock_path, mock_mkdir, mock_makedir):
        """ setup """
        mock_path.return_value = True
        mock_mkdir.return_value = None
        mock_makedir.return_value = None
        config_product = ConfigParser.RawConfigParser()
        config_product.add_section("main")
        config_product.set("main", COOKBOOK_NAME, COOKBOOK_URL)
        config_product.set("main", COOKBOOK_CHILD1, COOKBOOK_CHILD_URL1)
        config_product.set("main", COOKBOOK_CHILD2, COOKBOOK_CHILD_URL2)
        Config.CONFIG_COOKBOOK = config_product
        Config.CONFIG_MODULES = config_product
        config_package = ConfigParser.RawConfigParser()
        config_package.add_section("main")
        config_package.set("main", PRODUCT_MURANO_NAME, PRODUCT_MURANO_NAME)
        Config.CONFIG_MURANOAPPS = config_package
        Config.NID = {}

    def tearDown(self):
        """ tear down  """
        self.mock_open.reset_mock()

    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_product_package(self, mock_open,  mock_exists, mock_copy):
        """test the object is correctly built"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        product = Product(PRODUCT_NAME, PRODUCT_VERSION)
        product_package = ProductPackage(product)
        self.assertEquals(product_package.get_product().product_name,
                          PRODUCT_NAME)
        self.assertEquals(len(product_package.get_cookbooks()), 1)
        self.mock_open.reset_mock()

    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_product_murano_package(self, mock_open,  mock_exists, mock_copy):
        """test the object is correctly built"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=MANIFEST).return_value,
            mock.mock_open(read_data=MANIFEST).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=MANIFEST).return_value
        ]
        product = Product(PRODUCT_MURANO_NAME, PRODUCT_VERSION)
        product_package = ProductPackage(product)
        self.assertEquals(product_package.get_product().product_name,
                          PRODUCT_MURANO_NAME)
        self.mock_open.reset_mock()

    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_product_package_child_chef(self, mock_open,
                                        mock_exists, mock_copy):
        """test the object is correctly built"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        metadatas = {}
        metadatas["installator"] = "Chef"
        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        product_package = ProductPackage(product)
        self.assertEquals(product_package.get_product().product_name,
                          PRODUCT_NAME)
        self.assertEquals(len(product_package.get_cookbooks()), 2)
        self.mock_open.reset_mock()

    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    @mock.patch('json.loads')
    def test_product_package_child_puppet(self, mock_json, mock_open,
                                          mock_exists, mock_copy):
        """test the object is correctly built"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        mock_json.return_value = METADATA_JSON
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=METADATA_JSON_STR).return_value,
            mock.mock_open(read_data=METADATA_JSON_STR).return_value,
            mock.mock_open(read_data=METADATA_JSON_STR).return_value,
            mock.mock_open(read_data=METADATA_JSON_STR_NO_CHILD).return_value,
            mock.mock_open(read_data=METADATA_JSON_STR_NO_CHILD).return_value,
            mock.mock_open(read_data=METADATA_JSON_STR_NO_CHILD).return_value,
        ]
        metadatas = {}
        metadatas["installator"] = "Puppet"
        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        product_package = ProductPackage(product)
        self.assertEquals(product_package.get_product().product_name,
                          PRODUCT_NAME)
        self.assertEquals(len(product_package.get_cookbooks()), 3)
        self.mock_open.reset_mock()
