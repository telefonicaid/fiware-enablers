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

import argparse


from packagegenerator.model.product_package import ProductPackage
from packagegenerator.model.product import Product
from packagegenerator.util.configuration import Config
import distutils.util as util2
import packagegenerator.util.utils_file as utils


PRODUCTANDRELEASE_BODY = "productAndReleaseDto"
BODY_PRODUCT = "product"
BODY_PRODUCTNAME = "name"
BODY_PRODUCTVERSION = "version"
BODY_METADATAS = "metadatas"
BODY_METADATA_KEY = "key"
BODY_METADATA_VALUE = "value"

DEPRECATED_PRODUCTS = ["MRCoAP", "marketplace", "SQLDatabaseLibrary",
                       "mongodbconfig", "mongodbshard", "mongos",
                       "orion-dbcluster",
                       "synchronization_fives", "repository", "mediawiki",
                       "haproxy", "wstore"]
NO_TOUCH = ["iotagent", "python"]


def main(argv=None):
    """
    Getting parameters
    :param argv:
    """
    parser = argparse.ArgumentParser(description='Testing product installation using paasmanager')
    parser.add_argument("-u", "--os-username", dest='user',
                        help='valid username', required=True)
    parser.add_argument("-p", "--os-password", dest='password',
                        help='valid password', required=True)
    parser.add_argument("-t", "--os-tenant-id", dest='tenant_id',
                        help="user tenant_id", required=True)
    parser.add_argument("-r", "--os-region-name", dest='region_name',
                        default='Spain2', help='the name of region')
    parser.add_argument("-k", "--os-auth-url", dest="auth_url",
                        default='http://cloud.lab.fiware.org:4731/v2.0',
                        help='url to keystone <host or ip>:<port>/v2.0')
    parser.add_argument("-g", "--os-upload", dest="upload",
                        default="False",
                        help='To upload to github?')
    parser.add_argument("-U", "--os-user_github", dest="user_github",
                        default='None',
                        help='user github')
    parser.add_argument("-P", "--os-password_github", dest="password_github",
                        default='None',
                        help='password github')

    args = parser.parse_args()

    create_murano_packages(auth_url=args.auth_url,
                           tenant_id=args.tenant_id,
                           user=args.user,
                           password=args.password,
                           region_name=args.region_name,
                           user_github=args.user_github,
                           password_github=args.password_github,
                           upload=args.upload)


def create_murano_packages(auth_url, tenant_id, user, password, region_name,
                           user_github, password_github, upload):
    """
    It creates the murano package and uploades it into github.
    :param auth_url:
    :param tenant_id:
    :param user:
    :param password:
    :param region_name:
    :param user_github:
    :param password_github:
    :return:
    """
    Config(auth_url, user, password, tenant_id, region_name)
    allproductreleases = Config.Clients.get_product_releases()

    for product_xml in allproductreleases[PRODUCTANDRELEASE_BODY]:

        product = get_product(product_xml)
        if product.product_name in DEPRECATED_PRODUCTS:
            continue
        product.get_image_metadata()
        package_murano = ProductPackage(product)
        package_murano.generate_package()

    if util2.strtobool(upload):
        update_into_github(user_github, password_github)


def get_product(product_json):
    """
    It obtains the product object from a JSON
    :param product_json:
    :return:
    """
    product_name = product_json[BODY_PRODUCT][BODY_PRODUCTNAME]
    product_version = product_json[BODY_PRODUCTVERSION]
    metadatas = {}
    attributes = {}
    if product_json[BODY_PRODUCT].get(BODY_METADATAS):
        for metadata_json in product_json[BODY_PRODUCT][BODY_METADATAS]:
            try:
                metadata_key = metadata_json[BODY_METADATA_KEY]
                metadata_value = metadata_json[BODY_METADATA_VALUE]
            except TypeError:
                metadatas_json = product_json[BODY_PRODUCT][BODY_METADATAS]
                metadata_key = metadatas_json[BODY_METADATA_KEY]
                metadata_value = metadatas_json[BODY_METADATA_VALUE]
            metadatas[metadata_key] = metadata_value

        if "attributes" in product_json[BODY_PRODUCT].keys():
            for att_json in product_json[BODY_PRODUCT]["attributes"]:
                try:
                    att_key = att_json[BODY_METADATA_KEY]
                    att_value = att_json[BODY_METADATA_VALUE]
                except TypeError:
                    att_json = product_json[BODY_PRODUCT]["attributes"]
                    att_key = att_json[BODY_METADATA_KEY]
                    att_value = att_json[BODY_METADATA_VALUE]
                att_key = att_key.split("::")[-1]
                attributes[att_key] = att_value
    return Product(product_name, product_version, load_data=True,
                   metadatas=metadatas, attributes=attributes)


def update_into_github(user_github, password_github):
    """
    It update the packages into github.
    :param user_github:
    :param password_github:
    :return:
    """
    branch_str = utils.create_branch("./../")
    URL_REPO = "https://api.github.com/repos/telefonicaid/fiware-enablers"
    utils.create_github_pull_request(URL_REPO, user_github,
                                     password_github, branch_str)
    utils.delete_branch(branch_str)


if __name__ == "__main__":
    main()
