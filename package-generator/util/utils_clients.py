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

import osclients
from sdcclient.client import SDCClient
from paasmanagerclient.client import PaaSManagerClient
from muranoclient import client
from keystoneclient.v2_0 import Client as KeystoneClient
import uuid

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
        :return nothing
        """
        self.auth_url = auth_url
        self.user = user
        self.password = password
        self.tenant_id = tenant_id
        self.region_name = region_name
        self.glance_client = self._get_glance_client()
        self.sdc_client = self._get_sdc_client()
        self.paas_manager_client = self._get_paas_manager_client()
        self.murano_client = self._get_murano_client()

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

    def _get_paas_manager_client(self):
        """
        It obtains a client for accessing to SDC.
        :return: the sdc client
        """
        return PaaSManagerClient(self.user, self. password, self.tenant_id,
                         self.auth_url, self.region_name)

    def _get_murano_client(self):
        """
        It obtains the Murano Client.
        :return: murano client
        """
        self.keystone_client = KeystoneClient(username=self.user, password=self.password, tenant_id=self.tenant_id,
                                              auth_url=self.auth_url, region=self.region_name)
        endpoint = self.get_murano_endpoint_from_keystone(self.region_name, "application-catalog", "publicURL" )
        token = self.keystone_client.auth_ref['token']['id']
        return client.Client(
            version='1', endpoint=endpoint, token=token)

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
        client = self.sdc_client.\
            getProductAndReleaseResourceClient()
        allproductreleases, _ = client.get_allproductandrelease()
        return allproductreleases

    def get_abstract_templates(self):
        """
        It obtains the abstract templates in PaaS Manager.
        :return: the list with the abstract templates.
        """
        client = self.paas_manager_client.getEnvironmentResourceClient()
        environments, _ = client.list_abstract_environments()
        return environments

    def create_env_template(self, template_name, description):
        return self.murano_client.env_templates.create(
            {"name": template_name, "description_text": description,
            "is_public": True})

    def create_app_in_template(self, env_template_id, data):
        """
        It creates an application in a template in Murano.
        :param env_template_id: the environment template ID.
        :param data: the application information.
        :return: the modified template.
        """
        return self.murano_client.env_templates.create_app(env_template_id, data)

    def list_abstract_template_murano(self):
        """
        It lists the abstract templates in Murano.
        :return: the list with the abstract templates.
        """
        return self.murano_client.env_templates.list()

    def list_packages_murano(self):
        """
        It lists the packages deployed in Murano.
        :return: the list with the packages
        """
        array = []
        arr = self.murano_client.packages.list()
        for i in arr:
            array.append(i)
        return array

    def get_murano_endpoint_from_keystone(self, region_name, service_type, endpoint_type):
        """
        Get the endpoint of Murano from Keystone Service Catalog
        :param region_name: Name of the region
        :param service_type: Type of service (Endpoint name)
        :param endpoint_type: Type of the URL to look for
        :return: the endpoint
        """
        endpoint = None
        for service in self.keystone_client.auth_ref['serviceCatalog']:
            if service['name'] == service_type:
                for endpoint in service['endpoints']:
                    if endpoint['region'] == region_name:
                        endpoint = endpoint[endpoint_type]
                        break
                break
        return endpoint

