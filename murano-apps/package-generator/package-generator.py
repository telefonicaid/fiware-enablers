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
from scripts.getnids.getnid import NID
from scripts.getnids import getnid

logger = get_logger(__name__)

PRODUCTANDRELEASE_BODY = "productAndReleaseDto"
BODY_PRODUCT = "product"
BODY_PRODUCTNAME = "name"
BODY_PRODUCTVERSION = "version"
BODY_METADATAS = "metadatas"
BODY_METADATA_KEY = "key"
BODY_METADATA_VALUE = "value"


def main(argv=None):
    """
    Getting parameters
    :param argv:
    """
    parser = argparse.ArgumentParser(description=
                                     ('Testing product '
                                      'installation using paasmanager'))
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

    args = parser.parse_args()
    logger.info(args)

    create_murano_packages(auth_url=args.auth_url,
                           tenant_id=args.tenant_id,
                           user=args.user,
                           password=args.password,
                           region_name=args.region_name)


def create_murano_packages(auth_url, tenant_id, user, password, region_name):

    logger.info("==========================================================\n")
    logger.info("Platform: " + auth_url + ". Region: " + region_name +
                ". Username: " + user + " Tenant-ID: " + tenant_id + "\n")
    logger.info("==========================================================\n")

    logger.info("SDC call to get the list of products available in catalog")

    sdc_client = SDCClient(user, password, tenant_id, auth_url, region_name)
    productandrelease_client = sdc_client.getProductAndReleaseResourceClient()
    allproductreleases, _ = productandrelease_client.get_allproductandrelease()

    config_products = load_config_products()
    nids = get_all_nids()
    config_cookbooks = load_config_cookbooks()
    for product_xml in allproductreleases[PRODUCTANDRELEASE_BODY]:
        product = get_product(product_xml)
        nid = get_nid(product, nids, config_products)
        product.set_nid(nid)
        image = product.get_image_metadata()
        if image is not None and product.is_enabler():
            package_murano = ProductPackage(product, config_cookbooks)
            package_murano.generate_manifest()
            package_murano.generate_class()
            package_murano.generate_template()


def get_nid(product, nids, config_products):
    try:
        nid_aux = config_products.get("main", product.get_product_name())
        return nids.get(nid_aux)
    except:
        return None


def load_config_products():

    config_product = ConfigParser.RawConfigParser()
    config_product.read('settings/product_names')
    return config_product


def load_config_cookbooks():
    config_cookbooks = ConfigParser.RawConfigParser()
    config_cookbooks.read('settings/cookbooks_urls')
    return config_cookbooks


def get_product(product_json):
    product_name = product_json[BODY_PRODUCT][BODY_PRODUCTNAME]
    product_version = product_json[BODY_PRODUCTVERSION]
    metadatas = {}
    if product_json[BODY_PRODUCT].get(BODY_METADATAS):
    # Checks if there are metadatas in the product
        for metadata_json in product_json[BODY_PRODUCT][BODY_METADATAS]:
            try:
                metadata_key = metadata_json[BODY_METADATA_KEY]
                metadata_value = metadata_json[BODY_METADATA_VALUE]
            except TypeError:
                metadata_key = product_json[BODY_PRODUCT][BODY_METADATAS]
                [BODY_METADATA_KEY]
                metadata_value = product_json[BODY_PRODUCT][BODY_METADATAS]
                [BODY_METADATA_VALUE]
            metadatas[metadata_key] = metadata_value
    return Product(product_name, product_version, metadatas)


def get_all_nids():
    all_nids = {}
    nid = NID()
    params = {}
    params['--wikitext'] = False

    for chapter in nid.TYPE.keys():
        params['--type'] = chapter
        params[chapter] = True
        nids = getnid.processingnid(params).values()[0]
        all_nids.update(nids)
        params[chapter] = False
    return all_nids


if __name__ == "__main__":
    main()
