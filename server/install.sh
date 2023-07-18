APP_NAME=pirobot
DAEMON_NAME=pirobotd

pyinstaller manage.py $(ls handlers/* | grep -v __init__.py | grep -v base.py | grep -v __pycache__ | grep -v .pyc | sed -e 's/handlers\/\(\w\+\).py/ --hidden-import  handlers.\1/g') --collect-all cv2 -F -n $DAEMON_NAME

sudo cp dist/$DAEMON_NAME /usr/local/bin/
sudo mkdir -p /etc/$APP_NAME
sudo cp -rf config /etc/$APP_NAME/
sudo cp -rf assets /etc/$APP_NAME/
sudo cp pirobot.config /etc/$APP_NAME/

sudo adduser www-data spi
sudo adduser www-data gpio
sudo adduser www-data dialout
sudo adduser www-data video
sudo adduser www-data audio
sudo mkdir -p /var/www
sudo chown www-data /var/www/
sudo chgrp www-data /var/www/

sudo cp pirobot.service /etc/systemd/system/