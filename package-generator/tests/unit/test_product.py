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
from model.product import Product
from util.configuration import Config
import ConfigParser

PRODUCT_NAME = "product"
PRODUCT_VERSION = "productVersion"
COOKBOOK_NAME = "product"
COOKBOOK_URL = "http://product.git"
COOKBOOK_CHILD = "child"
PRODUCT_VERSION = "productVersion"
PRODUCT_NAME_NID = "productnid"
NID = "NID"

PRODUCT_NAME_OTHER = "other"


class TestProduct(unittest.TestCase):
    """Class to test basic operations for the Product class"""

    def setUp(self):
        config_cookbook = ConfigParser.RawConfigParser()
        config_cookbook.add_section("main")
        config_cookbook.set("main", COOKBOOK_NAME, COOKBOOK_URL)
        Config.CONFIG_COOKBOOK = config_cookbook
        config_product = ConfigParser.RawConfigParser()
        config_product.add_section("main")
        config_product.set("main", PRODUCT_NAME, PRODUCT_NAME_NID)
        Config.CONFIG_PRODUCT = config_product
        Config.NID = {PRODUCT_NAME_NID: NID}

    def test_constructor(self):
        """test the object is correctly built"""
        metadatas = {}
        metadatas["key1"] = "value1"
        metadatas["key2"] = "value2"

        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        self.assertEquals(product.get_product_name(), PRODUCT_NAME)
        self.assertEquals(product.get_nid(), NID)
        self.assertEquals(product.is_enabler(), True)
        self.assertEquals(product.get_product_version(), PRODUCT_VERSION)
        self.assertEquals(len(product.get_product_metadatas()), 2)

    def test_no_nid(self):
        product = Product(PRODUCT_NAME_OTHER, PRODUCT_VERSION)
        self.assertEquals(product.get_product_name(), PRODUCT_NAME_OTHER)
        self.assertEquals(product.get_nid(), None)
        self.assertEquals(product.is_enabler(), False)
        self.assertEquals(product.get_product_version(), PRODUCT_VERSION)

    def test_image_metadata(self):
        """test obtaining a valid image"""
        metadatas = {}
        metadatas["image"] = "value1"

        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        self.assertIsNotNone(product.get_image_metadata())

    def test_not_image_metadata(self):
        """test obtaining the image which does not exist"""
        product = Product(PRODUCT_NAME, PRODUCT_VERSION)
        self.assertIsNone(product.get_image_metadata())

    def test_puppet_installator(self):
        """test obtaining the image which does not exist"""
        metadatas = {}
        metadatas["installator"] = "puppet"
        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        self.assertTrue(product.is_puppet_installator())

    def test_check_installator(self):
        """test obtaining the image which does not exist"""
        metadatas = {}
        metadatas["installator"] = "chef"
        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        self.assertEquals(product.get_installator(), "Chef")

    def test_check_no_installator(self):
        """test obtaining the image which does not exist"""
        product = Product(PRODUCT_NAME, PRODUCT_VERSION)
        self.assertIsNone(product.get_installator())

    def test_ports(self):
        """test the functionalities to get tcp and udp ports for the product"""
        metadatas = {}
        metadatas["open_ports"] = "1"
        metadatas["udp_open_ports"] = "1"

        product = Product(PRODUCT_NAME, PRODUCT_VERSION, metadatas)
        self.assertEquals(len(product.get_tcp_ports()), 2)
        self.assertEquals(len(product.get_udp_ports()), 1)
