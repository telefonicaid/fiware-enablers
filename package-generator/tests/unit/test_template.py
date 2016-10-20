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
from packagegenerator.model.template import Template
from packagegenerator.util.configuration import Config
import collections
import mock

TEMPLATE_NAME = "template"
TEMPLATE_DESCRIPTION = "description"

PRODUCT1 = "PRODUCT"
PRODUCT2 = "PRODUCT2"
VERSION = "vesrion"


class TestTemplate(unittest.TestCase):
    """Class to test basic operations for the Template class"""

    def test_constructor(self):
        """test the object is correctly built"""
        template = Template(TEMPLATE_NAME, TEMPLATE_DESCRIPTION)

        self.assertEquals(template.template_name, TEMPLATE_NAME)
        self.assertEquals(template.template_description, TEMPLATE_DESCRIPTION)
        self.assertIsNone(template.tiers)

    @mock.patch('packagegenerator.util.utils_clients.util_apis')
    def test_add_tier(self, mock_client):
        """ test adding a tier to the template """

        productRelease = collections.OrderedDict([(u'productName', PRODUCT1),
                                                  (u'version', VERSION)])
        tierDto = collections.OrderedDict([(u'name', "TIER"), (u'flavour', "flavour"),
                                           (u'image', "image"),
                                           (u'productReleaseDtos', productRelease)])
        template = Template(TEMPLATE_NAME, TEMPLATE_DESCRIPTION)
        template.template_id = "ID"

        class Object(object):
            pass
        newtemplate = Object()
        newtemplate.id = "ID"

        mock_client.create_env_template.return_value = newtemplate
        mock_client.get_image_name.return_value = "image"
        Config.Clients = mock_client

        template.add_tiers(tierDto)
        self.assertEquals(len(template.tiers), 1)
