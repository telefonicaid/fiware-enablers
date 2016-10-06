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
from model.product import Product
from model.tier import Tier
from util.configuration import Config
import collections
import mock

TIER_NAME = "tier"
FLAVOUR = "2"
IMAGE = "image"

PRODUCT1 = "PRODUCT"
PRODUCT2 = "PRODUCT2"
VERSION = "vesrion"


class TestTier(unittest.TestCase):
    """Class to test basic operations for the Tier class"""

    def test_constructor(self):
        """test the object is correctly built"""
        tier = Tier(TIER_NAME, FLAVOUR, IMAGE)

        self.assertEquals(tier.tier_name, TIER_NAME)
        self.assertEquals(tier.flavour, FLAVOUR)
        self.assertEquals(tier.image, IMAGE)
        self.assertIsNone(tier.products)

    @mock.patch('util.utils_clients.util_apis')
    def test_add_product(self, mock_client):
        """ test adding a product to the tier """
        productRelease = collections.OrderedDict([(u'productName', PRODUCT1),
                                                  (u'version', VERSION)])

        tier = Tier(TIER_NAME, FLAVOUR, IMAGE)

        class Object(object):
            """Object tests"""
            pass
        template = Object()
        template.instance = {
            "?": {
                "type": "io.murano.resources.FiwareMuranoInstance",
                "id": "ID"
            }
        }

        mock_client.create_app_in_template.return_value = template
        mock_client.get_image_name.return_value = "image"
        Config.Clients = mock_client

        tier.add_products_from_xml(productRelease, 'ID')
        self.assertEquals(tier.tier_name, TIER_NAME)
        self.assertEquals(tier.flavour, FLAVOUR)
        self.assertEquals(tier.image, IMAGE)
        self.assertIsNotNone(tier.products)
        self.assertEquals(len(tier.products), 1)
        self.assertEquals(tier.products[0].product_name, PRODUCT1)

    @mock.patch('util.utils_clients.util_apis')
    def test_add_products(self, mock_client):
        """ test adding two products to the tier"""
        productRelease = [collections.OrderedDict([(u'productName', PRODUCT1), (u'version', VERSION)]),
                          collections.OrderedDict([(u'productName', PRODUCT2), (u'version', VERSION)])]

        tier = Tier(TIER_NAME, FLAVOUR, IMAGE)

        class Object(object):
            pass
        template = Object()
        template.instance = {
            "?": {
                "type": "io.murano.resources.FiwareMuranoInstance",
                "id": "ID"
            }
        }

        mock_client.create_app_in_template.return_value = template
        mock_client.get_image_name.return_value = "image"
        Config.Clients = mock_client
        tier.add_products_from_xml(productRelease, 'ID')
        self.assertEquals(tier.tier_name, TIER_NAME)
        self.assertEquals(tier.flavour, FLAVOUR)
        self.assertEquals(tier.image, IMAGE)
        self.assertIsNotNone(tier.products)
        self.assertEquals(len(tier.products), 2)

    @mock.patch('util.utils_clients.util_apis')
    def test_to_json(self, mock_client):
        """ test transform a tier into a json """
        product = Product(TIER_NAME, FLAVOUR)
        tier = Tier(TIER_NAME, FLAVOUR, IMAGE)
        mock_client.get_image_name.return_value = "image"
        Config.Clients = mock_client
        jsonTier = tier.toJson(product, 'ID')
        self.assertEquals(jsonTier["name"], TIER_NAME)
