sed -i -e "s/XXX/${PASSWORD}/" /opt/fiware-enablers/package-generator/tests/acceptance/config.conf
sed -i -e "s/*log*//" /opt/fiware-enablers/package-generator/package-generator.py
/opt/fiware-enablers/package-generator/other.sh
nosetests --with-xunit --xunit-file /opt/test.xml  tests 

