#<a name="top"></a>Package Generator

[![License badge](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Build status](https://travis-ci.org/telefonicaid/fiware-enablers/package-generator.svg?branch=develop)
[![Coveralls](https://coveralls.io/repos/telefonicaid/fiware-enablers/package-generator/badge.svg?branch=develop&service=github)


* [Introduction](#introduction)
* [GEi overall description](#gei-overall-description)
* [Build and Install](#build-and-install)
* [API Overview](#api-overview)
* [Testing](#testing)
    * [Unit Tests](#unit-tests)
    * [End-to-end tests](#end-to-end-tests)
* [Advanced topics](#advanced-topics)
* [Support](#support)
* [License](#license)


## Introduction

The package generator is a tool for migrating from PaaS Manager to Murano. It involves mainly two functionalities:
- generate murano package from PaaS Manager products.
- generate Murano environment templates from PaaS Manager blueprint templates.

## Build and install
The following software must be installed (e.g. using apt-get on Debian and Ubuntu,
or with yum in CentOS):

- Python 2.7
- pip
- virtualenv

### Installation

The recommend installation method is using a virtualenv. Actually, the installation
process is only about the python dependencies, because the scripts do not need
installation.

1) Create a virtualenv 'ENV' invoking *virtualenv ENV*
2) Activate the virtualenv with *source ENV/bin/activate*
3) Install the requirements running *pip install -r requirements.txt
   --allow-all-external*

Now the system is ready to use. For future sessions, only the step2 is required.


## Running
### Generating Murano packages
The script package-generator.py script is used for generating Murano Packages from product uploaded in PaaS Manager and SDC. In addition, once the packages have been
generated, a new Pull Request is done to the fiware-enabler github repository with the new changes

 The following lines are shown by using the -h option
    usage: package-generator.py [-h] -u USER -p PASSWORD -t TENANT_ID
                            [-r REGION_NAME] [-k AUTH_URL] [-g UPLOAD]
                            [-ug USER_GITHUB] [-pg PASSWORD_GITHUB]

    Testing product installation using paasmanager

    optional arguments:
    -h, --help            show this help message and exit
    -u USER, --os-username USER
                        valid username for a keystone
    -p PASSWORD, --os-password PASSWORD
                        valid password for a keystone
    -t TENANT_ID, --os-tenant-id TENANT_ID
                        user tenant_id for a keystone
    -r REGION_NAME, --os-region-name REGION_NAME
                        the name of region for a keystone
    -k AUTH_URL, --os-auth-url AUTH_URL
                        url to keystone <host or ip>:<port>/v2.0
    -g UPLOAD, --os-upload UPLOAD
                        To upload to github?
    -ug USER_GITHUB, --os-user_github USER_GITHUB
                        user github
    -pg PASSWORD_GITHUB, --os-password_github PASSWORD_GITHUB
                        password github

### Generating Murano templates
This command is used for generating Murano templates from PaaS Manager. With the following command, you can get the help
for using it.

    usage: migrate-templates.py [-h] -u USER -p PASSWORD -t TENANT_ID
                            [-r REGION_NAME] [-k AUTH_URL]

    Migrating templates

    optional arguments:
        -h, --help            show this help message and exit
        -u USER, --os-username USER
                        valid username for a keystone
        -p PASSWORD, --os-password PASSWORD
                        valid password  for a keystone
        -t TENANT_ID, --os-tenant-id TENANT_ID
                        user tenant_id for a keystone
        -r REGION_NAME, --os-region-name REGION_NAME
                        the name of region for a keystone
        -k AUTH_URL, --os-auth-url AUTH_URL
                        url to keystone <host or ip>:<port>/v2.0


## Testing

### Unit tests
Unit tests are executed with the following command.
    nosetests --with-coverage --cover-package=./ --exe

## License

\(c) 2015-2016 Telefónica I+D, Apache License 2.0
