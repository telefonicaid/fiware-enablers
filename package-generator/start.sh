sed -i -e "s/XXX/${PASSWORD}/" /opt/fiware-enablers/package-generator/tests/acceptance/config.conf
sed -i -e "s/*log*//" /opt/fiware-enablers/package-generator/package-generator.py
sed -i -e "s/XXX/${PASSWORD}/" /opt/fiware-enablers/package-generator/other.sh
python setup.py install
/opt/fiware-enablers/package-generator/other.sh
