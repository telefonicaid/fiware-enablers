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
        self.auth_url = auth_url
        self.user = user
        self.password = password
        self.tenant_id = tenant_id
        self.region_name = region_name
        self.glance_client = self._get_glance_client()
        self.sdc_client = self._get_sdc_client()

    def _get_glance_client(self):
        clients = osclients.OpenStackClients(self.auth_url)
        clients.set_region(self.region_name)
        clients.set_credential(self.user, self. password,
                               tenant_id=self.tenant_id)
        return clients.get_glanceclient()

    def _get_sdc_client(self):
        return SDCClient(self.user, self. password, self.tenant_id,
                         self.auth_url, self.region_name)

    def _get_image_name(self, image_id):
        try:
            return self.glance_client.images.get(image_id).name
        except:
            return None
