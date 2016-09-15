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
import yaml
import ConfigParser
from os.path import join, isdir


class DeployPackagesTest(core.MuranoTestsCore, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(DeployPackagesTest, cls).setUpClass()
        cls.linux = core.CONF.murano.linux_image
        cls.flavor = core.CONF.murano.standard_flavor
        cls.keyname = core.CONF.murano.keyname
        cls.instance_type = core.CONF.murano.instance_type
        cls.config = load_config2_murano_apps("./settings/muranopackages_urls")

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

                'networks': {
                    "useFlatNetwork": False,
                    "primaryNetwork": None,
                    "useEnvironmentNetwork": False,
                    "customNetworks": [
                        {
                            "internalNetworkName": "node-int-net-01",
                            "?": {
                                "type": "io.murano.resources.ExistingNeutronNetwork",
                                "id": "1e26a1d725b44b639aef9e856577a70d"
                            }
                        }
                    ]
                },
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
                post_body[att[:-1]] = att[:-1]

        environment_name = environment_name + uuid.uuid4().hex[:5]
        environment = self.create_environment2(name=environment_name)
        print("environment")
        print(environment)
        session = self.create_session(environment)
        print(self.get_environment(environment))
        self.add_service(environment, post_body, session)
        self.deploy_environment(environment, session)
        self.wait_for_environment_deploy(environment)
        self.deployment_success_check(environment, port)

    def read_manifest(self, product_path):
        manifest_file = product_path + "/manifest.yaml"
        with open(manifest_file, "r") as fread:
            manifest = yaml.load(fread.read())
        return manifest

    def get_murano_name(self, murano_app):
        return self.config.get('main', murano_app)

    @mock.patch('murano.tests.functional.engine.config')
    def deploy_package(self, package_str, is_GE, mock_config):
        """It obtains the murano packages created and deploy then"""
        mock_config.load_config = load_config()
        self.linux = core.CONF.murano.linux_image
        self.flavor = core.CONF.murano.standard_flavor
        self.keyname = core.CONF.murano.keyname
        self.instance_type = core.CONF.murano.instance_type
        self.murano_apps_folder = core.CONF.murano.murano_apps_folder
        self.murano_package = package_str
        if is_GE == "GE":
            package_folder = os.path.join(self.murano_apps_folder,
                                          "murano-app-GE",
                                          self.murano_package)
        else:
            package_folder = os.path.join(self.murano_apps_folder,
                                          "murano-app-noGE",
                                          self.murano_package)

        manifest = self.read_manifest(package_folder)
        package_id = manifest["FullName"]
        tags = manifest["Tags"]
        requires = manifest.get("Require")

        package = self.get_package(package_id)

        if package:
            self.delete_package(package)

        self.upload_app(package_folder,
                        self.murano_package,
                        {"is_public": True, "tags": tags})

        images = ["base_ubuntu_14.04"]
        atts = {}

        if requires:
            for require in requires:
                if not self.get_package(require):
                    folder_required = os.path.join(self.murano_apps_folder,
                                                   "murano-app-noGE",
                                                   self.get_murano_name(require))
                    self.upload_app(folder_required,
                                    self.get_murano_name(require),
                                    {"is_public": True,
                                    "tags": ["tag"]})

        for tag in tags:
            if "images" in tag:
                tag = tag[7:len(tag)]
                images = tag.split(';')
            if "attributes" in tag:
                tag = tag[11:len(tag)]
                atts = tag.split(';')

        for image in images:
            if image == "base_ubuntu_12.04":
                if len(images) == 1:
                    image = "base_ubuntu_14.04"
                else:
                    continue
            self.linux = image
            self._test_deploy(self.murano_package, package_id, 22, atts)
            self.purge_environments()

    def delete_package(cls, package):
        """It deletes the package in murano."""
        cls.murano_client().packages.delete(package.id)

    def create_environment2(cls, name=None):
        """Creates Murano environment with random name.
        :param name: Environment name
        :return: Murano environment
        """
        if not name:
            name = cls.rand_name('MuranoTe')
        environment = cls.murano_client().environments.create({
            "regionConfigs": {
                "Spain2": {
                    "agentRabbitMq": {
                        "host": "murano.lab.fiware.org",
                        "login": "guest",
                        "password": "guest"
			        }
		        }
	        } , 'name': name, "region": "Spain2"})
        cls._environments.append(environment)
        return environment

    def get_package(self, package_to_add):
        """It obtains the package from murano."""
        for package in \
                self.murano_client().packages.list(include_disabled=True):
            if package.fully_qualified_name == package_to_add:
                return package


murano_group = cfg.OptGroup(name='murano', title="murano")

MuranoGroup = [
    cfg.StrOpt('murano_apps_folder',
               default='.',
               help="Murano apps folder")
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


def _add_tests(generator):
    def class_decorator(cls):
        """Add tests to `cls` generated by `generator()`."""
        for f, input, input2 in generator():
            test = lambda self, i=input, i2=input2, f=f: f(self, i, i2)
            test.__name__ = "test_%s(%r)" % (f.__name__, input)
            setattr(cls, test.__name__, test)
        return cls
    return class_decorator


def _test_pairs():
    load_config()
    MURANO_APP_DISCARDED = ["SQLDatabaseLibrary"]
    murano_apps_folder = CONF.murano.murano_apps_folder
    folder = os.path.join(murano_apps_folder, "murano-app-GE")
    murano_packages = [f for f in listdir(folder) if
                       isdir(join(folder, f))]
    for murano_package in murano_packages:
        if murano_package in MURANO_APP_DISCARDED:
            continue
        yield DeployPackagesTest.deploy_package, murano_package, "GE"

    folder = os.path.join(murano_apps_folder, "murano-app-noGE")
    murano_packages = [f for f in listdir(folder) if
                       isdir(join(folder, f))]
    for murano_package in murano_packages:
        if murano_package in MURANO_APP_DISCARDED:
            continue
        yield DeployPackagesTest.deploy_package, murano_package, "noGE"

DeployPackagesTest = _add_tests(_test_pairs)(DeployPackagesTest)


def load_config2_murano_apps(file):
        """
        It loads the configuration file
        :param file: The configuration file
        :return: nothing
        """
        config_product = ConfigParser.RawConfigParser()
        config_product.read(file)
        return config_product

if __name__ == "__main__":
    unittest.main()
