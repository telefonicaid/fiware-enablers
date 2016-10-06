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

from util.configuration import Config
from model.product import Product
import uuid


class Tier():
    """This class represents the tier.
    """
    def __init__(self, tier_name, flavour, image, products=None):
        """
        :param tier_name: the tier name
        :param flavour: the flavour
        :param image: the image
        :param products: the products
        :return: nothing
        """
        self.tier_name = tier_name
        self.flavour = flavour
        self.image = image
        self.products = products

    def add_products_from_xml(self, productReleaseDtos, template_id):
        """
        It add products to the tier from XML file.
        :param productReleaseDtos: the XML with the product information
        :param new_template_id: the template ID
        :return:
        """
        if isinstance(productReleaseDtos, list):
            for productXML in productReleaseDtos:
                self._add_product(productXML)
        else:
            self._add_product(productReleaseDtos)

        self._create_murano_app(template_id)

    def _add_product(self, productXML):
        if not self.products:
            self.products = []
        product = Product(productXML["productName"], productXML["version"])
        self.products.append(product)

    def _create_murano_app(self, new_template_id):
        instance_id = None
        for product in self.products:
            template = Config.Clients.create_app_in_template(new_template_id, self.toJson(product, instance_id))
            instance_id = template.instance["?"]["id"]

    def toJson(self, product, instance_id):
        image = self._get_image_name(self.image)
        data = {}
        if instance_id:
            data["instance"] = {
                "?": {
                    "type": "io.murano.resources.FiwareMuranoInstance",
                    "id": instance_id
                }
            }
        else:
            data["instance"] = {
                "?": {
                    "type": "io.murano.resources.FiwareMuranoInstance",
                    "id": str(uuid.uuid4())
                },
                "flavor": self.flavour,
                "image": image,
                "assignFloatingIp": True,
                'name': self.tier_name,

                'networks': {
                    "useFlatNetwork": False,
                    "primaryNetwork": None,
                    "useEnvironmentNetwork": False,
                    "customNetworks": [
                        {
                            "internalNetworkName": "node-int-net-01",
                            "?": {
                                "type": "io.murano.resources.ExistingNeutronNetwork",
                                "id": "1e26a1d725b44b639aef9e856577a70d"
                            }
                        }
                    ]
                }
            }
        data["name"] = product.product_name
        data["port"] = 22
        data["?"] = {
            "type": product._get_productid_murano(),
            "id": str(uuid.uuid4())
        }

        return data

    def _get_image_name(self, image):
        return Config.Clients.get_image_name(image)
