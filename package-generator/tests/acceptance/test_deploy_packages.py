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
from muranoclient import client as mclient
import keystoneclient.v2_0 as keystoneclientv2
import keystoneclient.v3 as keystoneclientv3
import mock
import os
import unittest
from os import listdir
from oslo_config import cfg
import yaml
import ConfigParser
from os.path import join, isdir
import re


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


    def _get_service(self, environment_name, package_name, port, murano_instance, atts=None, vol=None):

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
                            "externalNetworkName": "public-ext-net-01",
                            "?": {
                                "type": "io.murano.resources.ExistingNeutronNetwork",
                                "id": "1e26a1d725b44b639aef9e856577a70d"
                            },
                        }
                    ]
                },
                "?": {
                    "type": murano_instance,
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

       # if vol:
       #    post_body["instance"]["volumes"] = volume_id


        return post_body

    def _get_service_no_instance(self, environment_name, package_name, port, atts=None):
        post_body = {
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

        return post_body

    def _test_deploy(self, environment_name, package_name, port, atts, region, murano_instance):
        """
        It deploys an enviornment.
        :param environment_name:  environment name
        :param package_name:  package name
        :param port: port to be opened
        :return:
        """
        post_body = self._get_service(environment_name, package_name, port, murano_instance, atts)
        environment_name = environment_name + uuid.uuid4().hex[:5]
        environment = self.create_environment_region(name=environment_name, region=region)
        session = self.create_session(environment)
        self.add_service(environment, post_body, session)
        self.deploy_environment(environment, session)
        self.wait_for_environment_deploy(environment)
        self.deployment_success_check(environment, port)

    def create_environment_region(self, name=None, region=None):
        """Creates Murano environment for a particular region.
        :param name: Environment name
        :param region: the region
        :return: Murano environment
        """
        if not name:
            name = self.rand_name('MuranoTe')

        args = {"name": name}
        if region:
            args["region"] = region
        environment = self.murano_client().environments.create(args)
        self._environments.append(environment)
        return environment

    def read_manifest(self, product_path):
        manifest_file = product_path + "/manifest.yaml"
        with open(manifest_file, "r") as fread:
            manifest = yaml.load(fread.read())
        return manifest

    def get_murano_name(self, murano_app):
        return self.config.get('main', murano_app)

    @mock.patch('murano.tests.functional.engine.config')
    def deploy_package(self, package_str, is_GE, region, murano_instance, mock_config):
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

            if package_str == "Demo":
            self.deploy_demo()
            return

        manifest = self.read_manifest(package_folder)
        package_id = manifest["FullName"]
        tags = manifest["Tags"]
        requires = manifest.get("Require")
        self._upload_app(package_id, package_folder, tags, requires)
        images = ["base_ubuntu_14.04"]
        atts = {}

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
            self._test_deploy(self.murano_package, package_id, 22, atts, region, murano_instance)
            self.purge_environments()

    def delete_package(cls, package):
        """It deletes the package in murano."""
        cls.murano_client_admin().packages.delete(package.id)

    def get_package(self, package_to_add):
        """It obtains the package from murano."""
        for package in \
                self.murano_client_admin().packages.list(include_disabled=True):
            if package.fully_qualified_name == package_to_add:
                return package

    def _upload_app(self, package_id, package_folder, tags, requires):
        package = self.get_package(package_id)

        if package:
            self.delete_package(package)

        self.upload_app_admin(package_folder,
                        self.murano_package,
                        {"is_public": True, "tags": tags})

        if requires:
            for require in requires:
                if not self.get_package(require):
                    folder_required = os.path.join(self.murano_apps_folder,
                                                   "murano-app-noGE",
                                                   self.get_murano_name(require))
                    self.upload_app_admin(folder_required,
                                    self.get_murano_name(require), {"is_public": True, "tags": ["tag"]})

    @mock.patch('murano.tests.functional.engine.config')
    def deploy_demo(self, mock_config):
        mock_config.load_config = load_config()
        self.murano_package = "Demo"
        package_folder = os.path.join(self.murano_apps_folder,
                                          self.murano_package)

        manifest = self.read_manifest(package_folder)
        package_id = manifest["FullName"]
        tags = manifest["Tags"]
        requires = manifest.get("Require")

        self._upload_app(package_id, package_folder, tags, requires)
        images = ["base_ubuntu_14.04"]
        atts = {}
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


        environment_name = self.murano_package + uuid.uuid4().hex[:5]
        environment = self.create_environment(name=environment_name)
        session = self.create_session(environment)

        apache_demo = self._get_service("Apache", "io.murano.apps.apache.ApacheHttpServer", 22, "io.murano.resources.FiwareMuranoInstance")
        self.add_service(environment, apache_demo, session)
        apache_demo_id= apache_demo["?"]["id"]

        mysql_demo = self._get_service("MySQL", "io.murano.databases.MySql", 22, "io.murano.resources.FiwareMuranoInstance")
        self.add_service(environment, mysql_demo, session)
        mysql_demo_id = mysql_demo["?"]["id"]

        service_demo = self._get_service_no_instance(self.murano_package, package_id, 22, atts)
        service_demo["apache"] = apache_demo_id
        service_demo["database"] = mysql_demo_id

        self.add_service(environment, service_demo, session)

        self.deploy_environment(environment, session)
        self.wait_for_environment_deploy(environment)
        self.deployment_success_check(environment, 22)
        self.purge_environments()


    def keystone_client_admin(cls):
        region = CONF.murano.region_name
        if re.match(".*/v3/?$", CONF.murano.auth_url):
            ksclient = keystoneclientv3
        else:
            ksclient = keystoneclientv2
        return ksclient.Client(username=CONF.murano.admin_user,
                               password=CONF.murano.admin_password,
                               tenant_name=CONF.murano.admin_tenant,
                               auth_url=CONF.murano.auth_url,
                               region_name=region)

    def murano_client_admin(cls):
        murano_url = cls.get_murano_url()
        return mclient.Client('1',
                              endpoint=murano_url,
                              token=cls.keystone_client_admin().auth_token)

    def upload_app_admin(cls, app_dir, name, tags):
        """Zip and upload application to Murano

        :param app_dir: Unzipped dir with an application
        :param name: Application name
        :param tags: Application tags
        :return: Uploaded package
        """
        zip_file_path = cls.zip_dir(os.path.dirname(__file__), app_dir)
        cls.init_list("_package_files")
        cls._package_files.append(zip_file_path)
        return cls.upload_package_admin(
            name, tags, zip_file_path)

    def upload_package_admin(cls, package_name, body, app):
        """Uploads a .zip package with parameters to Murano.

        :param package_name: Package name in Murano repository
        :param body: Categories, tags, etc.
                     e.g. {
                           "categories": ["Application Servers"],
                           "tags": ["tag"]
                           }
        :param app: Correct .zip archive with the application
        :return: Package
        """
        files = {'{0}'.format(package_name): open(app, 'rb')}
        package = cls.murano_client_admin().packages.create(body, files)
        cls.init_list("_packages")
        cls._packages.append(package)
        return package

murano_group = cfg.OptGroup(name='murano', title="murano")

MuranoGroup = [
    cfg.StrOpt('murano_apps_folder',
               default='.',
               help="Murano apps folder"),
    cfg.StrOpt('admin_user',
               default='user_admin',
               help="user_admin"),
    cfg.StrOpt('admin_password',
               default='user_admin',
               help="user_admin"),
    cfg.StrOpt('admin_tenant',
               default='user_admin',
               help="user_admin")
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
        for f, input, input2, input3, input4 in generator():
            def test(self, i=input, i2=input2, i3=input3, i4=input4, f=f): return f(self, i, i2, i3, i4)
            test.__name__ = "test_%s(%r)" % (f.__name__, input)
            setattr(cls, test.__name__, test)
        return cls
    return class_decorator


def _test_pairs():
    load_config()
    MURANO_APP_DISCARDED = ["SQLDatabaseLibrary"]
    murano_apps_folder = CONF.murano.murano_apps_folder
    folder = os.path.join(murano_apps_folder, "murano-app-GE")

    yield DeployPackagesTest.deploy_package, "Demo", "noGE", "Spain2", \
              "io.murano.resources.FiwareMuranoInstance"


    murano_packages = [f for f in listdir(folder) if
                       isdir(join(folder, f))]
    for murano_package in murano_packages:
        if murano_package in MURANO_APP_DISCARDED:
            continue
        yield DeployPackagesTest.deploy_package, murano_package, "GE", "Spain2", \
              "io.murano.resources.FiwareMuranoInstance"

    folder = os.path.join(murano_apps_folder, "murano-app-noGE")
    murano_packages = [f for f in listdir(folder) if
                       isdir(join(folder, f))]
    for murano_package in murano_packages:
        if murano_package in MURANO_APP_DISCARDED:
            continue
        yield DeployPackagesTest.deploy_package, murano_package, "noGE", "Spain2", \
              "io.murano.resources.FiwareMuranoInstance"


    yield DeployPackagesTest.deploy_package, "Tomcat", "noGE", "Zurich2", \
          "io.murano.resources.LinuxMuranoInstance"


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
