from setuptools import setup, find_packages
from pip.req import parse_requirements
from os.path import join as pjoin

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)
# > requirements_list is a list of requirement; e.g. ['requests==2.6.0', 'Fabric==1.8.3']
requirements_list = [str(ir.req) for ir in install_reqs]
requirements = parse_requirements("requirements.txt", session=False)

print [(ir.req, ir.link) for ir in requirements]   
 

setup(
  name='package_generator',
  install_requires=requirements_list,
  packages=find_packages(),
  version="0.0.3",
  license='Apache 2.0',
  url='https://github.com/telefonicaid/fiware-enablers/package-generator',
  classifiers=[
        "License :: OSI Approved :: Apache Software License", ],
)
