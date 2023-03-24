# PiRobot
https://pirobot.net/

# Install
```
sudo apt update
sudo apt install git
mkdir git
cd git
https://github.com/ivan-marchand/pirobot.git
cd pirobot/server

sudo apt install python3-pip
pip install pipenv
export PATH=$PATH:~/.local/bin

pipenv lock --python python3
pipenv install --system

./install.sh

sudo systemctl enable pirobot
sudo apt install espeak
```