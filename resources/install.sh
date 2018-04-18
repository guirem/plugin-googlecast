touch /tmp/dependancy_googlecast_in_progress
echo 0 > /tmp/dependancy_googlecast_in_progress
echo "Launch install of googlecast dependancy"
sudo apt-get update
echo 20 > /tmp/dependancy_googlecast_in_progress
sudo apt-get install -y python3 python-dev build-essential
echo 50 > /tmp/dependancy_googlecast_in_progress
sudo apt-get install -y python-requests python3-pip
echo 75 > /tmp/dependancy_googlecast_in_progress
cd pychromecast
sudo pip3 install -r requirements.txt
echo 100 > /tmp/dependancy_googlecast_in_progress
echo "Everything is successfully installed!"
rm /tmp/dependancy_googlecast_in_progress
