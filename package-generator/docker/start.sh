python setup.py install
sed -i -e "s/XXX/${ADMIN_PASSWORD}/" /opt/fiware-enablers/package-generator/tests/acceptance/config.conf
sed -i -e "s/YYY/${PASSWORD}/" /opt/fiware-enablers/package-generator/tests/acceptance/config.conf
sed -i -e "s/*log*//" /opt/fiware-enablers/package-generator/packagegenerator/package-generator.py
/opt/fiware-enablers/package-generator/other.sh
nosetests --with-xunit --xunit-file /opt/test.xml  tests 

