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

import osclients
from sdcclient.client import SDCClient


class util_apis():
    """This class have some utils for accessing to APIS"""

    def __init__(self, auth_url, user, password, tenant_id, region_name):
        """
        Constructor for Util Apis.
        :param auth_url: the keystone url.
        :param user: the user
        :param password: the password
        :param tenant_id: the tenant ID
        :param region_name: the region
        """
        self.auth_url = auth_url
        self.user = user
        self.password = password
        self.tenant_id = tenant_id
        self.region_name = region_name
        self.glance_client = self._get_glance_client()
        self.sdc_client = self._get_sdc_client()

    def _get_glance_client(self):
        """
        It obtains the glance client
        :return: the glance client
        """
        clients = osclients.OpenStackClients(self.auth_url)
        clients.set_region(self.region_name)
        clients.set_credential(self.user, self. password,
                               tenant_id=self.tenant_id)
        return clients.get_glanceclient()

    def _get_sdc_client(self):
        """
        It obtains a client for accessing to SDC.
        :return: the sdc client
        """
        return SDCClient(self.user, self. password, self.tenant_id,
                         self.auth_url, self.region_name)

    def get_image_name(self, image_id):
        """
        It gets an image name from an ID
        :param image_id: the ID of the image
        :return: the image name.
        """
        try:
            return self.glance_client.images.get(image_id).name
        except:
            return None

    def get_product_releases(self):
        """
        It obtains the product releases.
        :return: Array with product releases
        """
        productandrelease_client = self.sdc_client.\
        getProductAndReleaseResourceClient()
        allproductreleases, _ = productandrelease_client.get_allproductandrelease()
        return allproductreleases
