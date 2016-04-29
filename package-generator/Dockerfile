FROM ubuntu
RUN apt-get update && apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb 
RUN git clone https://github.com/telefonicaid/fiware-enablers /opt/fiware-enablers
WORKDIR /opt/fiware-enablers/package-generator
RUN pip install nose pytz
RUN pip install -r requirements.txt
RUN pip install -r tests-requirements.txt
COPY other.sh  /opt/fiware-enablers/package-generator/other.sh
COPY start.sh /opt/fiware-enablers/package-generator/start.sh
CMD ./start.sh

