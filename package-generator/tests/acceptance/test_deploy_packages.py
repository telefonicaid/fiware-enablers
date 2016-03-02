# Copyright (c) 2016 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

import murano.tests.functional.engine.manager as core
import murano.tests.functional.engine.config as config
import mock
import os
import unittest
from os import listdir
from oslo_config import cfg
import re

from os.path import join, isdir


class DeployPackagesTest(core.MuranoTestsCore, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(DeployPackagesTest, cls).setUpClass()
        cls.linux = core.CONF.murano.linux_image
        cls.flavor = core.CONF.murano.standard_flavor
        cls.keyname = core.CONF.murano.keyname
        cls.instance_type = core.CONF.murano.instance_type

    @classmethod
    def tearDownClass(cls):
        """
        It remove everything existing
        :return: nothing
        """
        try:
            cls.purge_environments()
        except Exception as e:
            raise e

    def _test_deploy(self, environment_name, package_name, port, atts):
        """
        It deploys an enviornment.
        :param environment_name:  environment name
        :param package_name:  package name
        :param port: port to be opened
        :return:
        """
        post_body = {
            "instance": {
                "flavor": self.flavor,
                "image": self.linux,
                "keyname": self.keyname,
                "assignFloatingIp": True,
                'name': environment_name,
                "?": {
                    "type": "io.murano.resources.FiwareMuranoInstance",
                    "id": str(uuid.uuid4())
                },
            },
            "name": environment_name,
            "port": port,
            "?": {
                "type": package_name,
                "id": str(uuid.uuid4())
            }
        }
        if atts:
            for att in atts:
                post_body[att] = att

        environment_name = environment_name + uuid.uuid4().hex[:5]
        environment = self.create_environment(name=environment_name)
        session = self.create_session(environment)
        self.add_service(environment, post_body, session)
        self.deploy_environment(environment, session)
        self.wait_for_environment_deploy(environment)
        self.deployment_success_check(environment, port)

    @mock.patch('murano.tests.functional.engine.config')
    def deploy_package(self, package_str, mock_config):
        """It obtains the murano packages created and deploy then"""
        mock_config.load_config = load_config()
        self.linux = core.CONF.murano.linux_image
        self.flavor = core.CONF.murano.standard_flavor
        self.keyname = core.CONF.murano.keyname
        self.instance_type = core.CONF.murano.instance_type
        self.murano_apps_folder = core.CONF.murano.murano_apps_folder
        self.murano_package = package_str
        tags = []
        package = self.get_package(self.murano_package)
        if package:
            self.delete_package(package)
            tags = package.tags

        package_folder = self.murano_apps_folder + self.murano_package

        tags.append({"is_public", True})
        uploaded_package = self.upload_app(package_folder,
                                           self.murano_package,
                                           tags)
        package_id = uploaded_package.class_definitions[0]

        images = ["base_ubuntu_14.04"]
        atts = {}
        tags = uploaded_package.tags
        for tag in tags:
            if "images" in tag:
                tag = tag[7:len(tag)]
                images = tag.split(';')
            if "attributes" in tag:
                tag = tag[11:len(tag)]
                atts = tag.split(';')

        for image in images:
            if image == "base_ubuntu_12.04":
                if len(image) == 1:
                    image = "base_ubuntu_14.04"
                else:
                    continue
            self.linux = image
            self._test_deploy(self.murano_package, package_id, 22, atts)
            self.purge_environments()

    def delete_package(cls, package):
        """It deletes the package in murano."""
        cls.murano_client().packages.delete(package.id)

    def get_package(self, package_to_add):
        """It obtains the package from murano."""
        for package in \
                self.murano_client().packages.list(include_disabled=True):
            if package.name == package_to_add:
                return package


murano_group = cfg.OptGroup(name='murano', title="murano")

MuranoGroup = [
    cfg.StrOpt('murano_apps_folder',
               default='.',
               help="Murano apps folder"),

]

CONF = cfg.CONF


def load_config():
    """ It loads the config.conf file as configuration """
    __location = os.path.realpath(os.path.join(os.getcwd(),
                                  os.path.dirname(__file__)))
    path = os.path.join(__location, "config.conf")
    if os.path.exists(path):
        CONF([], project='muranointegration', default_config_files=[path])

    config.register_config(CONF, murano_group, MuranoGroup)


def add_tests(generator):
    def class_decorator(cls):
        """Add tests to `cls` generated by `generator()`."""
        for f, input in generator():
            test = lambda self, i=input, f=f: f(self, i)
            test.__name__ = "test_%s(%r)" % (f.__name__, input)
            setattr(cls, test.__name__, test)
        return cls
    return class_decorator


def _test_pairs():
    load_config()
    murano_apps_folder = CONF.murano.murano_apps_folder
    murano_packages = [f for f in listdir(murano_apps_folder) if
                       isdir(join(murano_apps_folder, f))]
    for murano_package in murano_packages:
        yield DeployPackagesTest.deploy_package, murano_package

DeployPackagesTest = add_tests(_test_pairs)(DeployPackagesTest)


if __name__ == "__main__":
    unittest.main()
