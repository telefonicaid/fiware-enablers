FROM ubuntu
RUN apt-get update && sudo apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb mysql-server
RUN git clone https://github.com/telefonicaid/fiware-enablers /opt/fiware-enablers
WORKDIR /opt/fiware-enablers/package-generator
RUN sed -i -e "s/-e//" /opt/fiware-enablers/package-generator/requirements.txt
COPY start.sh /opt/fiware-enablers/package-generator/start.sh
RUN pip install pytz
RUN pip install --upgrade -r requirements.txt
RUN pip install -r tests-requirements.txt
RUN pip install nose
CMD ./start.sh
