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
PRODUCT_IMAGE = "image"
PRODUCT_INSTALLATOR = "installator"
PUPPET_INSTALLATOR = "Puppet"
TCP_PORTS = "open_ports"
UDP_PORTS = "udp_open_ports"
SSH_PORT = "22"
NID = "nid"
FILTER_IMAGE = "hi"

from util.configuration import Config


class Product():
    """This class represents the product.
    """
    def __init__(self, product_name, product_version, metadatas={},
                 attributes=[]):
        """
        :param product_name: the product name
        :param product_version: the release version
        :param metadatas: a set of metadatas
        :return: nothing
        """
        self.product_name = product_name
        self.is_murano_app = self.is_murano_app_oficial()
        self.product_name = self.get_product_name(product_name)
        self.cookbook_name = product_name
        self.product_version = product_version
        self.metadatas = metadatas
        self.installator = self._get_installator()
        self.nid = self._get_nid_from_catalogue()
        self.images = self._get_images_names()
        self.attributes = attributes

    def get_image_metadata(self):
        """
        It obtains the metadata image
        :return: the image name
        """
        image = None
        if PRODUCT_IMAGE in self.metadatas.keys():
            value = self.metadatas.get(PRODUCT_IMAGE)
            if value is not None and FILTER_IMAGE not in value:
                image = value
        return image

    def _get_nid_from_catalogue(self):
        """
        It obtains the NID from the catalogue
        :return: nid
        """
        try:
            nid_aux = Config.CONFIG_PRODUCT_NIDS.get("main",
                                                     self.product_name)
            return Config.NID.get(nid_aux)
        except:
            return None

    def get_tcp_ports(self):
        """
        It obtains the tcp ports for the product.
        :return: ports
        """
        ports = []
        if TCP_PORTS in self.metadatas.keys():
            value = self.metadatas.get(TCP_PORTS)
            ports = value.split()
        if SSH_PORT not in ports:
            ports.append(SSH_PORT)
        return ports

    def get_port(self):
        """
        It obtains a port from the product.
        :return: port
        """
        if TCP_PORTS in self.metadatas.keys():
            value = self.metadatas.get(TCP_PORTS)
            ports = value.split()
            if ports:
                return ports[0]
        return None

    def get_udp_ports(self):
        """
        It obtains the udp ports for the product.
        :return: ports
        """
        ports = []
        if UDP_PORTS in self.metadatas.keys():
            value = self.metadatas.get(UDP_PORTS)
            ports = value.split()
        return ports

    def get_nid_metadata(self):
        """
        It obtains the metadata image
        :return: the image name
        """
        nid = ''
        if NID in self.metadatas.keys():
            value = self.metadatas.get(NID)
            nid = value
        return nid

    def is_enabler(self):
        """
        It checks if the product is a FIWARE enabler.
        :return: True/False
        """
        if self.nid is not None:
            return True
        return False

    def is_puppet_installator(self):
        """
        It checks if the installator is Puppet
        :return: True/False
        """
        if PUPPET_INSTALLATOR in self.installator:
            return True
        return False

    def _get_installator(self):
        """
        It returns the type of installator
        :return: the installator
        """
        installator = None
        if PRODUCT_INSTALLATOR in self.metadatas.keys():
            value = self.metadatas.get(PRODUCT_INSTALLATOR)
            installator = value[0].upper() + value[1:]
        return installator

    def _get_images_names(self):
        """
        It obtains the image names associated to the
        products.
        :return: array with the image names
        """
        if not self.is_enabler():
            return None
        images_str = self.get_image_metadata()
        if not images_str:
            return None
        images = images_str.split(' ')
        images_names = []
        for image in images:
            name = Config.Clients.get_image_name(image)
            if name:
                images_names.append(name)
        return images_names

    def is_murano_app_oficial(self):
        """
        It checks if the package already exists in murano package
        repository from openstack.
        :return:
        """
        try:
            Config.CONFIG_MURANOAPPS.get('main', self.product_name)
            fiware_cookbooks = True
        except:
            fiware_cookbooks = False
        return fiware_cookbooks

    def get_murano_app_name(self):
        """
        It gets the murano package name in the oficial repository.
        :return:
        """
        return Config.CONFIG_MURANOAPPS.get('main', self.product_name)

    def get_product_name(self, name):
        """
        It obtains the product name in case required.
        :param name:  product name
        :return: product name changed
        """
        if self.is_murano_app:
            try:
                return Config.CONFIG_MURANOAPPS.get('main', name)
            except:
                return name
        try:
            return Config.CONFIG_PACKAGE_NAME.get('main', name)
        except:
            return name

    def get_cookbook_name(self, name):
        """
        It obtains the cookbook name in case required.
        :param name:  cookbook name
        :return: cookbook name changed
        """
        try:
            return Config.CONFIG_PRODUCT_NAMES.get('main', name)
        except:
            return name
