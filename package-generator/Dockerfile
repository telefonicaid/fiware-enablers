FROM ubuntu
RUN apt-get update && sudo apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb mysql-server
RUN git clone https://github.com/telefonicaid/fiware-enablers /opt/fiware-enablers
WORKDIR /opt/fiware-enablers/package-generator
RUN pip install -r requirements.txt
RUN pip install -r tests-requirements.txt
RUN pip install nose
COPY other.sh  /opt/fiware-enablers/package-generator/other.sh
COPY start.sh /opt/fiware-enablers/package-generator/start.sh
CMD ./start.sh

