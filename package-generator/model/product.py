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
    def __init__(self, product_name, product_version, metadatas={}):
        """
        :param product_name: the product name
        :param product_version: the release version
        :param metadatas: a set of metadatas
        :return:
        """
        self.product_name = product_name
        self.product_version = product_version
        self.metadatas = metadatas
        self.nid = self._get_nid_from_catalogue()

    def get_product_name(self):
        """
        It returns the product name.
        :return: product name
        """
        return self.product_name

    def get_product_version(self):
        """
        It returs the product version.
        :return:
        """
        return self.product_version

    def get_product_metadatas(self):
        """
        It returns the product metadatas.
        :return:
        """
        return self.metadatas

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
        try:
            nid_aux = Config.CONFIG_PRODUCT.get("main", self.get_product_name())
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

    def get_nid(self):
        """
        It obtains the product nid.
        :return: nid
        """
        return self.nid

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
        nid = self.get_nid()
        if nid is not None:
            return True
        return False

    def is_puppet_installator(self):
        """
        It checks if the installator is Puppet
        :return: True/False
        """
        installator = self.get_installator()
        if PUPPET_INSTALLATOR in installator:
            return True
        return False

    def get_installator(self):
        """
        It returns the type of installator
        :return:
        """
        installator = None
        if PRODUCT_INSTALLATOR in self.metadatas.keys():
            value = self.metadatas.get(PRODUCT_INSTALLATOR)
            installator = value[0].upper() + value[1:]
        return installator
