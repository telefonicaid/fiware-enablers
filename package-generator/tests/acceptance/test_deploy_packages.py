# Copyright (c) 2015 OpenStack Foundation
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
from os import listdir
from oslo_config import cfg

from os.path import join, isdir


class DeployPackagesTest(core.MuranoTestsCore):

    @classmethod
    def setUpClass(cls):
        super(DeployPackagesTest, cls).setUpClass()
        cls.linux = core.CONF.murano.linux_image
        cls.flavor = core.CONF.murano.standard_flavor
        cls.keyname = core.CONF.murano.keyname
        cls.instance_type = core.CONF.murano.instance_type

    @classmethod
    def tearDownClass(cls):
        try:
            cls.purge_environments()
            cls.purge_uploaded_packages()
        except Exception as e:
            raise e

    def _test_deploy(self, environment_name, package_name, port):
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

        environment_name = environment_name + uuid.uuid4().hex[:5]
        environment = self.create_environment(name=environment_name)
        session = self.create_session(environment)
        self.add_service(environment, post_body, session)
        try:
            self.deploy_environment(environment, session)
            self.wait_for_environment_deploy(environment)
            self.deployment_success_check(environment, port)
            print "Deployment OK"
        except Exception as e:
            print "Error " + e.message + ": " +\
                  (self.murano_client().deployments.list(environment.id)[-1].
                   result['result']['message'])


    @mock.patch('murano.tests.functional.engine.config')
    def test_deploys(self, mock_config):
        """It obtains the murano packages created and deploy then"""
        mock_config.load_config = self.load_config()
        self.linux = core.CONF.murano.linux_image
        self.flavor = core.CONF.murano.standard_flavor
        self.keyname = core.CONF.murano.keyname
        self.instance_type = core.CONF.murano.instance_type
        self.murano_apps_folder = core.CONF.murano.murano_apps_folder
        files = [f for f in listdir(self.murano_apps_folder) if
                 isdir(join(self.murano_apps_folder, f))]
        for folder in files:
            print folder
            package = self.upload_app('./../../../../../../../../../murano-apps/'
                            + folder, folder, {"tags": ["tag"]})
            tag_images = package.tags[len(package.tags)-1]
            if ';' in tag_images:
                images = tag_images.split(';')
                for image in images:
                    self.linux = image
                    self._test_deploy(folder,
                              'io.murano.conflang.chef.' + folder, 22)
            else:
                self._test_deploy(folder,
                              'io.murano.conflang.chef.' + folder, 22)
            self.purge_environments()
            self.purge_uploaded_packages()

    def load_config(self):
        __location = os.path.realpath(os.path.join(os.getcwd(),
                                      os.path.dirname(__file__)))
        path = os.path.join(__location, "config.conf")
        if os.path.exists(path):
            CONF([], project='muranointegration', default_config_files=[path])

        config.register_config(CONF, murano_group, MuranoGroup)

murano_group = cfg.OptGroup(name='murano', title="murano")

MuranoGroup = [
    cfg.StrOpt('murano_apps_folder',
               default='.',
               help="Murano apps folder"),
    cfg.StrOpt('auth_url',
               default='http://127.0.0.1:5000/v2.0/',
               help="keystone url"),
    cfg.StrOpt('user',
               default='admin',
               help="keystone user"),
    cfg.StrOpt('password',
               default='pass',
               help="password for keystone user"),
    cfg.StrOpt('tenant',
               default='admin',
               help='keystone tenant'),
    cfg.StrOpt('keyname',
               default='',
               help='name of keypair for debugging'),
    cfg.StrOpt('murano_url',
               default='http://127.0.0.1:8082/v1/',
               help="murano url"),
    cfg.StrOpt('standard_flavor',
               default='m1.medium',
               help="flavor for sanity tests"),
    cfg.StrOpt('advanced_flavor',
               default='m1.large',
               help="flavor for advanced tests"),
    cfg.StrOpt('linux_image',
               default='default_linux',
               help="image for linux services"),
    cfg.StrOpt('instance_type',
               default='io.murano.resources.LinuxMuranoInstance',
               help="murano instance type"),
    cfg.StrOpt('docker_image',
               default='ubuntu14.04-x64-docker',
               help="image for docker applications"),
    cfg.StrOpt('windows_image',
               default='default_windows',
               help="image for windows services"),
    cfg.StrOpt('hdp_image',
               default="hdp-sandbox",
               help="image for hdp-sandbox"),
    cfg.StrOpt('kubernetes_image',
               default="ubuntu14.04-x64-kubernetes",
               help="image for kubernetes"),
    cfg.StrOpt('region_name', help="region name for services")
]

CONF = cfg.CONF
