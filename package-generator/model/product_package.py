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
import shutil
import errno
import os
from util import utils_file as utils
from model.cookbook import Cookbook

PACKAGES_FOLDER = "./../murano-apps"
PACKAGE_TEMPLATE_CLASS = "template/PackageTemplate/Classes/GE_name.yaml"
PACKAGE_TEMPLATE_MANIFEST = "template/PackageTemplate/manifest.yaml"
PACKAGE_TEMPLATE_PLAN = "template/PackageTemplate/Resources/" \
                        "DeployExample.template"
TCP = "tcp"
UDP = "udp"


class ProductPackage():
    """This class represents the product package to be converted
    into murano package.
    """
    def __init__(self, product):
        """
        It is the constructor.
        :param product:  The product.
        """
        self.product = product
        self.package_folder = (PACKAGES_FOLDER + "/" +
                               product.product_name + "/")
        self.package_classes = self.package_folder + "Classes/"
        self.package_classes_file = (self.package_classes +
                                     self.product.product_name + ".yaml")
        self.package_manifest = self.package_folder + "manifest.yaml"
        self.package_resources = self.package_folder + "Resources/"
        self.package_template = (self.package_resources + "Deploy" +
                                 product.product_name + ".template")
        self.cookbooks = self.get_all_cookbooks()
        self._generate_package_folder()

    def get_product(self):
        """
        It returns the product
        :return: product
        """
        return self.product

    def get_cookbooks(self):
        """
        It returns the associated cookboooks.
        :return: cookbooks
        """
        return self.cookbooks

    def _generate_package_folder(self):
        """
        It generates the murano package folder structure.
        :return:
        """
        if not os.path.exists(PACKAGES_FOLDER):
            os.makedirs(PACKAGES_FOLDER)
        if not os.path.exists(self.package_folder):
            os.makedirs(self.package_folder)
        if not os.path.exists(self.package_classes):
            os.makedirs(self.package_classes)
        if not os.path.exists(self.package_resources):
            os.makedirs(self.package_resources)
        self._copy_files_from_templates()

    def _copy_files_from_templates(self):
        """
        It copies based files from the Template folder.
        """
        try:
            shutil.copy(PACKAGE_TEMPLATE_CLASS, self.package_classes_file)
            shutil.copy(PACKAGE_TEMPLATE_MANIFEST, self.package_manifest)
            shutil.copy(PACKAGE_TEMPLATE_PLAN, self.package_template)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy("PackageTemplate", self.product.product_name)
            else:
                raise

    def generate_manifest(self):
        """
        It generates the package manifest.
        """
        utils.replace_word(self.package_manifest, "{GE_name}",
                           self.product.product_name)
        utils.replace_word(self.package_manifest, "{GE_installator}",
                           self.product.installator.lower())
        utils.replace_word(self.package_manifest, "{GE_images}",
                           self._get_images_str())

    def generate_class(self):
        """
        It generates the package class file.
        """
        utils.replace_word(self.package_classes_file,
                           "{GE_name}", self.product.product_name)
        utils.replace_word(self.package_classes_file,
                           "{GE_ports}", self._get_ports_str())
        utils.replace_word(self.package_classes_file,
                           "{GE_nid}", self.product.nid)

    def generate_template(self):
        """
        It generates the package Excecution Plan.
        :return:
        """
        utils.replace_word(self.package_template, "{GE_name}",
                           self.product.product_name)
        if self.product.is_puppet_installator():
            utils.replace_word(self.package_template, "{GE_recipe}", "install")
        else:
            utils.replace_word(self.package_template, "{GE_recipe}",
                               self.product.product_version+"_install")
        utils.replace_word(self.package_template, "{GE_installator}",
                           self.product.installator)
        utils.replace_word(self.package_template, "{GE_cookbooks}",
                           self.get_cookbooks_str())

    def _get_images_str(self):
        image_str = ''
        if self.product.images:
            for image in self.product.images:
                image_str = image_str + image + ";"
        return image_str

    def _get_ports(self, protocol):
        """
        It obtains the string with the ports for the Class file.
        :param protocol:
        :return:
        """
        ports_str = ''
        if protocol is TCP:
            ports = self.product.get_tcp_ports()
        else:
            ports = self.product.get_udp_ports()
        for port in ports:
            ports_str = (ports_str + (" " * 12) + "- ToPort: " + port + "\n" +
                         (" " * 14) + "FromPort: " + port + "\n" + (" " * 14) +
                         "IpProtocol: " + protocol + "\n" + (" " * 14) +
                         "External: true\n")
        return ports_str

    def _get_ports_str(self):
        """
        It obtains the string representation for tcp and udp ports for the
        Class file
        :return:
        """
        return self._get_ports("tcp") + self._get_ports("udp")

    def get_all_cookbooks(self):
        """
        It obtain all cookbooks associated to the product.
        :return: Cookbook array
        """
        cookbooks = []
        cookbook = Cookbook(self.product.product_name,
                            self.product.installator,
                            self.product.is_enabler())
        cookbooks.append(cookbook)

        for cookbook_child in cookbook.cookbook_childs:
            if not self._exists(cookbook_child.name, cookbooks):
                cookbooks.append(cookbook_child)
            if len(cookbook_child.cookbook_childs) != 0:
                cookbooks_in = cookbook_child.get_all_cookbooks_child()
                cookbooks.extend(x for x in cookbooks_in
                                 if not self._exists(x.name, cookbooks))
        return cookbooks

    def _exists(self, cookbook_name, cookbooks):
        for cookbook in cookbooks:
            if cookbook_name == cookbook.name:
                return True
        return False

    def get_cookbooks_str(self):
        """
        It returns the string representation for the cookbooks.
        :return: string representation
        """
        cookbooks_str = ''
        for cookbook in self.cookbooks:
            cookbooks_str = (cookbooks_str + (" " * 8) + "- " + cookbook.name +
                             " : " + cookbook.url + "\n")
        return cookbooks_str
