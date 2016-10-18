#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014-2016 Telefónica Investigación y Desarrollo, S.A.U
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
from model.template import Template
from util.configuration import Config


def main(argv=None):
    """
    Getting parameters
    :param argv:
    """
    parser = argparse.ArgumentParser(description='Migrating templates')
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

    args = parser.parse_args(argv)

    migrate_templates(auth_url=args.auth_url,
                      tenant_id=args.tenant_id,
                      user=args.user,
                      password=args.password,
                      region_name=args.region_name)


def migrate_templates(auth_url, tenant_id, user, password, region_name):
    """
    It migrates the abstract templates from PaaS Manager to Murano
    :param auth_url: the auth url
    :param tenant_id: the tenant_id
    :param user: the user
    :param password: the password
    :param region_name: the region
    :return:
    """
    Config(auth_url, user, password, tenant_id, region_name)
    templates = Config.Clients.get_abstract_templates()

    abstract_templates = Config.Clients.list_abstract_template_murano()
    murano_names = []

    for m in abstract_templates:
        murano_names.append(m.name)

    for tempXML in templates["environmentDto"]:
        if tempXML['name'] in murano_names:
            print("Template {0} already exists".format(tempXML['name']))
            continue
        else:
            template = Template(tempXML['name'], tempXML['description'], [])
            template.create_env_template()
            template.add_tiers(tempXML["tierDtos"])
            print template


if __name__ == "__main__":
    main()
