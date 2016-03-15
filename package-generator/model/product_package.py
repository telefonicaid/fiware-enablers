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
import shutil
import time
import os
from util import utils_file as utils
from model.cookbook import Cookbook

PACKAGES_FOLDER = "./../murano-apps"
PACKAGES_FOLDER_GE = os.path.join(PACKAGES_FOLDER, "murano-app-GE")
PACKAGES_FOLDER_NO_GE = os.path.join(PACKAGES_FOLDER, "murano-app-noGE")

PACKAGE_TEMPLATE_FOLDER = "template/PackageTemplate"
PACKAGE_TEMPLATE_CLASS = PACKAGE_TEMPLATE_FOLDER + "/Classes/GE_name.yaml"
PACKAGE_TEMPLATE_MANIFEST = PACKAGE_TEMPLATE_FOLDER + "/manifest.yaml"
PACKAGE_TEMPLATE_PLAN = (PACKAGE_TEMPLATE_FOLDER +
                         "/Resources/DeployExample.template")
TCP = "tcp"
UDP = "udp"
REPLACE_GE_NAME = "{GE_name}"
REPLACE_GE_INSTALLATOR = "{GE_installator}"
REPLACE_GE_RECIPE = "{GE_recipe}"
REPLACE_GE_COOKBOOKS = "{GE_cookbooks}"
REPLACE_GE_IMAGES = "{GE_images}"
REPLACE_GE_ATTS = "{GE_attributes}"
REPLACE_GE_ATTS_RESOURCE = "{GE_attributes_resource}"
REPLACE_GE_PORTS = "{GE_ports}"
REPLACE_GE_NID = "{GE_nid}"
REPLACE_BERKSFILE = "{GE_berksfile}"
COOKBOOK_FOLDER = "cookbooks/"
MURANO_APPS = COOKBOOK_FOLDER + "murano-apps/"
MURANO_APPS_URL = "https://github.com/openstack/murano-apps.git"


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
        if product.is_enabler():
            self.package_folder =\
                os.path.join(PACKAGES_FOLDER_GE, product.product_name)
        else:
            self.package_folder = \
                os.path.join(PACKAGES_FOLDER_NO_GE, product.product_name)
        self.package_manifest = \
            os.path.join(self.package_folder, "manifest.yaml")
        if self.product.is_murano_app:
            self._download_package_murano()

        self.package_classes = os.path.join(self.package_folder, "Classes")
        self.package_classes_file = self.get_class_name_file()
        self.package_resources = os.path.join(self.package_folder, "Resources")
        self.package_template = os.path.join(self.package_resources,
                                             "Deploy{0}.template".format(product.product_name))
        self.is_berksfile = False
        self.cookbooks = self.get_all_cookbooks()
        if not self.product.is_murano_app and self.cookbooks:
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
        self._check_folder_exists()
        if not os.path.exists(self.package_folder):
            os.makedirs(self.package_folder)
        if not os.path.exists(self.package_classes):
            os.makedirs(self.package_classes)
        if not os.path.exists(self.package_resources):
            os.makedirs(self.package_resources)
        self._copy_files_from_templates()

    def _check_folder_exists(self):
        if not os.path.exists(PACKAGES_FOLDER):
            os.makedirs(PACKAGES_FOLDER)
        if not os.path.exists(PACKAGES_FOLDER_GE):
            os.makedirs(PACKAGES_FOLDER_GE)
        if not os.path.exists(PACKAGES_FOLDER_NO_GE):
            os.makedirs(PACKAGES_FOLDER_NO_GE)
        if not os.path.exists(COOKBOOK_FOLDER):
            os.makedirs(COOKBOOK_FOLDER)

    def _download_package_dependence(self, dependence):
        """
        It download the packages from the official repository
        :return: nothing
        """
        self._download_package_folder(dependence)

    def _download_package_murano(self):
        """
        It download the packages from the official repository
        :return: nothing
        """
        self._download_package_folder(self.product.product_name)

    def _download_package_folder(self, folder):
        """
        It download the packages from the official repository
        :return: nothing
        """
        self._check_folder_exists()
        if not os.path.isdir(MURANO_APPS):
            utils.download_git_repo(MURANO_APPS_URL, MURANO_APPS)
        folder_out = os.path.join(PACKAGES_FOLDER_NO_GE, folder)
        folder_changed = utils.get_murano_app_name(folder)
        if folder_changed:
            folder = folder_changed
        folder_in = os.path.join(MURANO_APPS, folder, "package")
        if not os.path.exists(folder_out):
            shutil.copytree(folder_in, folder_out)

    def _copy_files_from_templates(self):
        """
        It copies based files from the Template folder.
        :return: nothing
        """
        try:
            shutil.copy(PACKAGE_TEMPLATE_CLASS, self.package_classes_file)
            shutil.copy(PACKAGE_TEMPLATE_MANIFEST, self.package_manifest)
            shutil.copy(PACKAGE_TEMPLATE_PLAN, self.package_template)
        except:
            raise

    def generate_manifest(self):
        """
        It generates the package manifest.
        :return: nothing
        """
        utils.replace_word(self.package_manifest, REPLACE_GE_NAME,
                           self.product.product_name)
        utils.replace_word(self.package_manifest, REPLACE_GE_INSTALLATOR,
                           self.product.installator.lower())
        utils.replace_word(self.package_manifest, REPLACE_GE_IMAGES,
                           self._get_images_str())
        if self.product.attributes:
            utils.replace_word(self.package_manifest, REPLACE_GE_ATTS,
                               ", \'{0}\'".format(self._get_attributes_str()))
        else:
            utils.replace_word(self.package_manifest, REPLACE_GE_ATTS, '')

    def update_manifest_no_ge(self):
        """
        It updates the product package files if required
        :return:
        """
        if not(self.product.images or self.product.attributes):
            return

        manifest_yaml = utils.read_yaml_local_file(self.package_manifest)
        if not manifest_yaml:
            return
        tags = manifest_yaml["Tags"]
        tags2 = []
        for tag in tags:
            if ("attributes" in tag) or ("images" in tag)\
                    or ("FIWARE_GE" in tag):
                continue
            tags2.append(tag)

        if self.product.attributes:
            tags2.append(self._get_attributes_str())
        if self.product.images:
            tags2.append(self._get_images_str())
        if self.product.is_enabler:
            tags2.append("FIWARE_GE")
        manifest_yaml["Tags"] = tags2

        utils.write_local_yaml(self.package_manifest, manifest_yaml)

    def generate_class(self):
        """
        It generates the package class file.
        :return: nothing
        """
        utils.replace_word(self.package_classes_file,
                           REPLACE_GE_NAME, self.product.product_name)
        utils.replace_word(self.package_classes_file,
                           REPLACE_GE_PORTS, self._get_ports_str())
        if self.product.nid:
            utils.replace_word(self.package_classes_file,
                               REPLACE_GE_NID, self.product.nid)
        else:
            utils.replace_word(self.package_classes_file,
                               REPLACE_GE_NID, '')
        utils.replace_word(self.package_classes_file, REPLACE_GE_ATTS_RESOURCE,
                           self._get_attributes_resource())
        utils.replace_word(self.package_classes_file, REPLACE_GE_ATTS,
                           self._get_attributes_class_str())
        utils.replace_word(self.package_classes_file, REPLACE_GE_INSTALLATOR,
                           self.product.installator.lower())

    def generate_template(self):
        """
        It generates the package Excecution Plan.
        :return: nothing
        """
        utils.replace_word(self.package_template, REPLACE_GE_NAME,
                           self.product.get_cookbook_name(self.product.product_name))
        if self.product.is_puppet_installator():
            if self.product.is_enabler():
                utils.replace_word(self.package_template,
                                   REPLACE_GE_RECIPE, "install")
            else:
                utils.replace_word(self.package_template,
                                   REPLACE_GE_RECIPE, "")
        else:
            if self.product.is_enabler():
                utils.replace_word(self.package_template, REPLACE_GE_RECIPE,
                                   self.product.product_version+"_install")
            else:
                utils.replace_word(self.package_template, REPLACE_GE_RECIPE,
                                   "default")
        utils.replace_word(self.package_template, REPLACE_GE_INSTALLATOR,
                           self.product.installator)
        utils.replace_word(self.package_template, REPLACE_GE_COOKBOOKS,
                           self.get_cookbooks_str())
        utils.replace_word(self.package_template, REPLACE_GE_ATTS,
                           self._get_attributes_template_str())
        utils.replace_word(self.package_template, REPLACE_BERKSFILE,
                           self._get_berksfile_str())

    def _get_images_str(self):
        """
        It obtains the string with the image information
        :return: the string
        """
        image_str = ''
        if self.product.images:
            image_str = ', images='
            leng = 0
            for image in self.product.images:
                if leng != 0:
                    image_str = image_str + ";" + image
                else:
                    image_str = image_str + image
                leng = leng + 1
        return image_str

    def _get_attributes_str(self):
        """
        It obtains the string with the attribute information for the manifest
        :return: the string
        """
        atts_str = ''
        if self.product.attributes:
            atts_str = "attributes="
            if self.product.attributes:
                for att in self.product.attributes:
                    atts_str = \
                        atts_str + "{0}:{1};".format(att,
                                                     self.product.attributes[att])
        return atts_str

    def _get_attributes_template_str(self):
        """
        It obtains the string with the attribute information for the template
        :return: the string
        """
        atts_str = ''
        port = self.product.get_port()
        if port:
            atts_str = atts_str + 'port: $port\n'
        if self.product.attributes:
            for key in self.product.attributes:
                atts_str = atts_str + (" " * 2) + key + ": $" + key + "\n"
        return atts_str

    def _get_berksfile_str(self):
        if self.is_berksfile:
            return "useBerkshelf: true"
        else:
            return ''

    def _get_attributes_resource(self):
        """
        It obtains the string with the attribute information for the class
        :return: the string
        """
        template_resource = \
            "- $template: $resources.yaml(\'Deploy{0}.template\')".\
            format(self.product.product_name)
        if not self.product.attributes:
            return template_resource
        template_resource = template_resource + ".bind(dict(\n"
        leng = len(self.product.attributes) - 1
        for key in self.product.attributes:
            if leng == 0:
                template_resource = \
                    template_resource + \
                    (" " * 16) + "{0} => $.{1}))".format(key, key)
            else:
                template_resource = \
                    template_resource +\
                    (" " * 16) + "{0} => $.{1},\n".format(key, key)
            leng = leng - 1

        return template_resource

    def _get_attributes_class_str(self):
        """
        It obtains the string with the attribute information fo the class
        :return: the string
        """
        atts_str = ''
        if self.product.attributes:
            for key in self.product.attributes:
                atts_str = atts_str + (" " * 2) + key + ":\n" +\
                    (" " * 4) + "Contract: $.string()\n" + \
                    (" " * 4) + "Default: \"" + self.product.attributes[key] +"\"\n"
        return atts_str

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
        return self._get_ports(TCP) + self._get_ports(UDP)

    def get_all_cookbooks(self):
        """
        It obtain all cookbooks associated to the product.
        :return: Cookbook array
        """
        cookbooks = []
        cookbook = Cookbook(self.product.cookbook_name,
                            self.product.installator,
                            self.product.is_enabler())
        if cookbook.url:
            cookbooks.append(cookbook)
            if cookbook.is_berksfile:
                self.is_berksfile = True
                return cookbooks

            for cookbook_child in cookbook.cookbook_childs:
                if (not self._exists(cookbook_child.name, cookbooks)
                        and cookbook_child.url):
                    cookbooks.append(cookbook_child)
                if len(cookbook_child.cookbook_childs) != 0:
                    cookbooks_in = cookbook_child.get_all_cookbooks_child()
                    cookbooks.extend(x for x in cookbooks_in
                                     if not self._exists(x.name, cookbooks))
        return cookbooks

    def _exists(self, cookbook_name, cookbooks):
        """
        It checks if the cookbook is already stored in the array.
        :param cookbook_name: the cookbook name
        :param cookbooks: the cookbook array
        :return: True/False
        """
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
            if cookbook.url:
                cookbooks_str = (cookbooks_str + (" " * 8) + "- " +
                                 cookbook.name + " : " + cookbook.url + "\n")
        return cookbooks_str

    def generate_package(self):
        """
        It generate all files for the murano package.
        :return: nothing
        """
        if self.product.is_murano_app:
            self.read_dependences()
            self.update_attributes()
            self.update_manifest_no_ge()
        else:
            if self.cookbooks:
                self.generate_manifest()
                self.generate_class()
                self.generate_template()

    def read_dependences(self):
        """
        It read and download the dependences from a murano pacakge.
        :return:
        """
        manifest_yaml = utils.read_yaml_local_file(self.package_manifest)
        requires = manifest_yaml.get("Require")
        if requires:
            for require in requires:
                app_name = utils.get_murano_app_name(require)
                if app_name:
                    self._download_package_dependence(app_name)

    def update_attributes(self):
        class_yaml = utils.read_yaml_local_file(self.package_classes_file)
        properties = class_yaml.get("Properties")
        attributes = {}
        if properties:
            for property in properties:
                if property == "instance":
                    continue
                else:
                    value = properties[property].get("default")
                    if not value:
                        value = ""
                    attributes[property] = value
            self.product.attributes.update(attributes)

    def get_class_name_file(self):
        package_classes_file = \
            os.path.join(self.package_classes,
                         "{0}.yaml".format(self.product.product_name))
        if self.product.is_murano_app:
            manifest_yaml = utils.read_yaml_local_file(self.package_manifest)
            classes = manifest_yaml.get("Classes")
            if classes:
                for classe in classes:
                    package_classes_file = os.path.join(self.package_classes,
                                                        classes[classe])
                    break
        return package_classes_file




