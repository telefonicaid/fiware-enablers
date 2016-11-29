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
- generate Murano package from PaaS Manager products.
- generate Murano environment templates from PaaS Manager blueprint templates.
- generate a Murano package from a json with the information

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
The package-generator.py script is used for generating Murano Packages from product uploaded in PaaS Manager and SDC. Once the packages have been
generated, a new Pull Request is done to the fiware-enabler github repository with the new changes. In addition, this script can be used also for
generating a concrete Murano package specifing its description

 The following lines are shown by using the -h option
    usage: package-generator.py [-h] -a ACTION -u USER -p PASSWORD -t TENANT_ID
                            [-r REGION_NAME] [-k AUTH_URL] [-g UPLOAD]
                            [-U USER_GITHUB] [-P PASSWORD_GITHUB] [-d PRODUCT_DESCRITION]

    Creating Murano packages from PaaS Manager

    optional arguments:
    -h, --help            show this help message and exit
    -a ACTION, --action, the action to be executed (generate_package or genarate_all_packages). Generate
    package action which create a concrete package from a description and generate_all_packages action
    will syncronize information from PaaS Manager and SDC.
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
                        True/False for uploading to github
    -U USER_GITHUB, --os-user_github USER_GITHUB
                        github user
    -P PASSWORD_GITHUB, --os-password_github PASSWORD_GITHUB
                        github password
    -d PRODUCT_DESCRIPTION, --description, a file containing the product description (for example product_example.json)

#### Generate a package
To generate a concreate package, we can use:

    package-generator.py  -a generate_package -d product_example.json -u myuser -p mypassword -t mytenant

where product_example.json contains the production description information including product name, version, metadata
and attributes as followed.
    {
	    "name": "my_product",
	    "version": "my_version",
	    "metadatas": {
		    "open_ports": "value1",
		    "image": "value1",
		    "nid": "nid",
		    "installator": "chef"
	    },
	    "attributes": {
		    "database": "value1",
		    "password": "value2"
	    }
    }

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
