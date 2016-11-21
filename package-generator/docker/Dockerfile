FROM ubuntu:14.04
ENV GIT_REVISION develop
RUN apt-get update && apt-get -y install python-pip python-dev \
  libmysqlclient-dev wget libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb 
RUN wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz
RUN tar xfz Python-2.7.11.tgz
WORKDIR /Python-2.7.11/
RUN ./configure --prefix /usr/local/lib/python2.7.11 --enable-ipv6
RUN make
RUN make install
RUN git clone https://github.com/telefonicaid/fiware-enablers /opt/fiware-enablers
WORKDIR /opt/fiware-enablers/package-generator
RUN git checkout ${GIT_REVISION}
RUN cat requirements.txt
ENV GLANCESYNC_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync.cfg
ENV GLANCESYNC_LOGGING_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync-logging.cfg
COPY fiware-glancesync.cfg /etc/fiware.d/etc/fiware-glancesync.cfg
COPY fiware-glancesync-logging.cfg /etc/fiware.d/etc/fiware-glancesync-logging.cfg
RUN pip install nose pytz
RUN pip install -r requirements.txt
RUN pip install -r tests-requirements.txt
COPY other.sh  /opt/fiware-enablers/package-generator/other.sh
COPY start.sh /opt/fiware-enablers/package-generator/start.sh
CMD ./start.sh

