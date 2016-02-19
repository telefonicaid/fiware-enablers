sed -i -e "s/XXX/${PASSWORD}/" /opt/fiware-enablers/package-generator/tests/acceptance/config.conf
sed -i -e "s/*log*//" /opt/fiware-enablers/package-generator/package-generator.py
python setup.py install
python package-generator.py -u admin -g False -t 00000000000003228460960090160000 -p ${PASSWORD}
nosetests tests 
