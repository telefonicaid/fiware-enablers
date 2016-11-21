#!/bin/bash

function include(){
    curr_dir=$(cd $(dirname "$0") && pwd)
    inc_file_path=$curr_dir/$1
    if [ -f "$inc_file_path" ]; then
        . $inc_file_path
    else
        echo -e "$inc_file_path not found!"
        exit 1
    fi
}
include "common.sh"


bash installer.sh -p sys -i "java-devel"

yum install wget

wget https://releases.wikimedia.org/mediawiki/1.27/mediawiki-1.27.1.tar.gz
tar -xvzf mediawiki-*.tar.gz
sudo mkdir /var/lib/mediawiki
sudo mv mediawiki-*/* /var/lib/mediawiki
cp /var/lib/mediawiki/includes/DefaultSettings.php /var/lib/mediawiki/LocalSettings.php
cd /var/www/html
sudo ln -s /var/lib/mediawiki mediawiki

