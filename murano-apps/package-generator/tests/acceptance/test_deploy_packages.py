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
from os import listdir
import shutil

from os.path import isfile, join, isdir


class DeployPackagesTest(core.MuranoTestsCore):

    @classmethod
    def setUpClass(cls):
        super(DeployPackagesTest, cls).setUpClass()
        cls.linux = core.CONF.murano.linux_image
        cls.flavor = core.CONF.murano.standard_flavor
        cls.keyname = core.CONF.murano.keyname
        cls.instance_type = core.CONF.murano.instance_type
        """Trying to overwrite the configuration file"""
        shutil.copy("config.conf", "./../../venv/lib/python2.7/site-packages/murano/tests/functional/engine")

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
        self.deploy_environment(environment, session)
        self.wait_for_environment_deploy(environment)
        self.deployment_success_check(environment, port)

    def test_deploys(self):
        """It obtains the murano packages created and deploy then"""
        files = [f for f in listdir("./../../Packages") if isdir(join("./../../Packages", f))]
        for folder in files:
            print folder
            self.upload_app('./../../../../../../../../Packages/'+folder,
                          folder, {"tags": ["tag"]})
            self._test_deploy(folder,
                          'io.murano.conflang.chef.'+folder, 22)
            self.purge_environments()
            self.purge_uploaded_packages()
