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
import ConfigParser

from sdcclient.client import SDCClient
from utils.logger_utils import get_logger
from model.product_package import ProductPackage
from model.product import Product



logger = get_logger(__name__)

PRODUCTANDRELEASE_BODY_ROOT = "productAndReleaseDto";
PRODUCTANDRELEASE_BODY_PRODUCT = "product";
PRODUCTANDRELEASE_BODY_PRODUCTNAME = "name";
PRODUCTANDRELEASE_BODY_PRODUCTVERSION = "version";
PRODUCTANDRELEASE_BODY_METADATAS = "metadatas";
PRODUCTANDRELEASE_BODY_METADATA_KEY = "key";
PRODUCTANDRELEASE_BODY_METADATA_VALUE = "value";
PRODUCTANDRELEASE_BODY_METADATA_INSTALLATOR = "installator";
PRODUCTANDRELEASE_BODY_METADATA_INSTALLATOR_CHEF_VALUE = "chef";



def main(argv=None):
    """
    Getting parameters
    :param argv:
    """
    parser = argparse.ArgumentParser(description='Testing product installation using paasmanager')
    parser.add_argument("-u", "--os-username", dest='user', help='valid username', required=True)
    parser.add_argument("-p", "--os-password", dest='password', help='valid password', required=True)
    parser.add_argument("-t", "--os-tenant-id", dest='tenant_id', help="user tenant_id", required=True)
    parser.add_argument("-r", "--os-region-name", dest='region_name', default='Spain2', help='the name of region')
    parser.add_argument("-k", "--os-auth-url", dest="auth_url", default='http://cloud.lab.fiware.org:4731/v2.0',
                        help='url to keystone <host or ip>:<port>/v2.0')

    args = parser.parse_args()
    logger.info(args)

    create_murano_packages (
                     auth_url=args.auth_url,
                     tenant_id=args.tenant_id,
                     user=args.user,
                     password=args.password,
                     region_name=args.region_name)

def create_murano_packages(auth_url, tenant_id, user, password, region_name):

    logger.info("========================================================================================\n")
    logger.info("Platform: " +  auth_url + ". Region: " + region_name + ". Username: " + user
                      + " Tenant-ID: " + tenant_id + "\n")
    logger.info("========================================================================================\n")

    logger.info("SDC call to get the list of products available in catalog")

    sdc_client = SDCClient(user, password, tenant_id, auth_url, region_name)
    productandrelease_client = sdc_client.getProductAndReleaseResourceClient()
    allproductreleases,_ = productandrelease_client.get_allproductandrelease()

    config_products = load_config_products()
    config_cookbooks = load_config_cookbooks()
    for i in allproductreleases[PRODUCTANDRELEASE_BODY_ROOT]:
        p = get_product(i)
        image = p.get_image_metadata()
        if image is not None and p.get_nid() is not '':
            package_murano = ProductPackage(p, config_cookbooks)
            package_murano.generate_manifest()
            package_murano.generate_class()
            package_murano.generate_template()

def load_config_products():

    config_product = ConfigParser.RawConfigParser()
    config_product.read('settings/product_names')
    return config_product


def load_config_cookbooks():
    config_cookbooks = ConfigParser.RawConfigParser()
    config_cookbooks.read('settings/cookbooks_urls')
    return config_cookbooks

def get_product(i):
    product_name = i[PRODUCTANDRELEASE_BODY_PRODUCT][PRODUCTANDRELEASE_BODY_PRODUCTNAME]
    product_version = i[PRODUCTANDRELEASE_BODY_PRODUCTVERSION]
    metadatas = {}
    if i[PRODUCTANDRELEASE_BODY_PRODUCT].get(PRODUCTANDRELEASE_BODY_METADATAS): # Checks if there are metadatas in the product
        for j in i[PRODUCTANDRELEASE_BODY_PRODUCT][PRODUCTANDRELEASE_BODY_METADATAS]:
            try :
               metadata_key = j[PRODUCTANDRELEASE_BODY_METADATA_KEY]
               metadata_value = j[PRODUCTANDRELEASE_BODY_METADATA_VALUE]
            except TypeError:
                metadata_key = i[PRODUCTANDRELEASE_BODY_PRODUCT][PRODUCTANDRELEASE_BODY_METADATAS][PRODUCTANDRELEASE_BODY_METADATA_KEY]
                metadata_value = i[PRODUCTANDRELEASE_BODY_PRODUCT][PRODUCTANDRELEASE_BODY_METADATAS][PRODUCTANDRELEASE_BODY_METADATA_VALUE]
            metadatas[metadata_key] = metadata_value
    return Product(product_name, product_version, metadatas)

if __name__ == "__main__":
    main()