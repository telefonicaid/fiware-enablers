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
from model.product_package import ProductPackage
from model.product import Product
import six
import io
from mock import patch
import mock
import ConfigParser
from sys import version_info

COOKBOOK_NAME = "product"
COOKBOOK_URL = "http://product.git"
COOKBOOK_CHILD = "child"
COOKBOOK_CHILD2 = "child2"
COOKBOOK_CHILD_URL = "http://child.git"
PRODUCT_VERSION = "productVersion"
metadata_product_child = "depends \'" + COOKBOOK_CHILD+ "\'"
metadata_product_child2 = "depends \'" + COOKBOOK_CHILD2+ "\'"
metadata_product_no_child = "other"

PRODUCT_NAME = "product"
PRODUCT_VERSION = "productVersion"

class TestProduct(unittest.TestCase):
    """Class to test basic operations for the Product class"""

    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    @mock.patch('os.makedirs')
    def setUp(self, mock_path, mock_mkdir, mock_makedir):
        mock_path.return_value = True
        mock_mkdir.return_value = None
        mock_makedir.return_value = None
        self.config = self.load_config_cookbooks()
        pass

    def tearDown(self):
        self.mock_open.reset_mock()
        pass

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
        product_package = ProductPackage(product, self.config)
        self.assertEquals(product_package.get_product().get_product_name(), PRODUCT_NAME)
        self.assertEquals(len(product_package.get_cookbooks()), 1)
        self.mock_open.reset_mock()

    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open', create=True)
    def test_product_package_child(self, mock_open,  mock_exists, mock_copy):
        """test the object is correctly built"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        self.mock_open = mock_open
        self.mock_open.side_effect = [
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value,
            mock.mock_open(read_data=metadata_product_no_child).return_value
        ]
        product = Product(PRODUCT_NAME, PRODUCT_VERSION)
        product_package = ProductPackage(product, self.config)
        self.assertEquals(product_package.get_product().get_product_name(), PRODUCT_NAME)
        self.assertEquals(len(product_package.get_cookbooks()), 2)
        self.mock_open.reset_mock()

    def load_config_cookbooks(self):
        config_cookbooks = ConfigParser.RawConfigParser()
        config_cookbooks.read('settings/cookbooks_url')
        return config_cookbooks
