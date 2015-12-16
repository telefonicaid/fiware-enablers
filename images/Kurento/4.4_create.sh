#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -q
sudo apt-get install -q -y wget

echo "deb http://ubuntu.kurento.org trusty kms6" | sudo tee /etc/apt/sources.list.d/kurento.list
wget -O - http://ubuntu.kurento.org/kurento.gpg.key | sudo apt-key add -
sudo apt-get update -q
sudo apt-get install -q -y kurento-media-server-6.0

wget http://turnserver.open-sys.org/downloads/v4.4.2.2/turnserver-4.4.2.2-debian-wheezy-ubuntu-mint-x86-64bits.tar.gz
tar xzf turnserver-4.4.2.2-debian-wheezy-ubuntu-mint-x86-64bits.tar.gz

sudo apt-get install -y -q libevent-core-2.0-5 libevent-extra-2.0-5 libevent-openssl-2.0-5 libevent-pthreads-2.0-5 libhiredis0.10 libmysqlclient18 libpq5

sudo dpkg -i coturn_4.4.2.2-1_amd64.deb

# Enable turn server
sudo tee <<-EOF /etc/default/coturn >/dev/null
TURNSERVER_ENABLED=1
EOF

sudo tee <<-EOF /etc/turnserver_check.sh
  #!/bin/bash

  # Get deployment info
  local_ip=\$(curl http://169.254.169.254/latest/meta-data/local-ipv4)
  public_ip=\$(curl http://169.254.169.254/latest/meta-data/public-ipv4)

  previous_public_ip=\$(cat /etc/turnserver.conf | grep "external-ip" | cut -d "=" -f 2 | cut -d "/" -f 1)

  # Update config file and restart service only when needed
  if [ \$public_ip == \$previous_public_ip ] ; then
    exit 0
  fi

  # Configure STUN/TURN
  TURN_USERNAME="fiware"
  TURN_PASSWORD="fiware"
  echo 'min-port=49152' > /etc/turnserver.conf
  echo 'max-port=65535' >> /etc/turnserver.conf
  echo 'fingerprint' >> /etc/turnserver.conf
  echo 'lt-cred-mech' >> /etc/turnserver.conf
  echo 'realm=kurento.org' >> /etc/turnserver.conf
  echo 'no-stdout-log' >> /etc/turnserver.conf
  echo "user=\$TURN_USERNAME:\$TURN_PASSWORD" >> /etc/turnserver.conf
  echo "external-ip=\$public_ip/\$local_ip" >> /etc/turnserver.conf

  # Restart Coturn
  /etc/init.d/coturn restart

  # Configure WebRTC
  echo "stunServerAddress=\$public_ip" > /etc/kurento/modules/kurento/WebRtcEndpoint.conf.ini
  echo "stunServerPort=3478" >> /etc/kurento/modules/kurento/WebRtcEndpoint.conf.ini

  # Restart KMS
  /etc/init.d/kurento-media-server-6.0 restart
EOF

sudo chmod +x /etc/turnserver_check.sh

sudo tee <<-EOF /etc/cron.d/turn >/dev/null
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
* *     * * *   root    /etc/turnserver_check.sh
@reboot root /etc/turnserver_check.sh
EOF

sudo /etc/init.d/coturn restart
sudo service kurento-media-server-6.0 restart

