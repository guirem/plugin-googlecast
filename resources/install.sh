touch /tmp/dependancy_googlecast_in_progress
echo 0 > /tmp/dependancy_googlecast_in_progress
echo "Launch install of googlecast dependancy"
echo "-- Updating repo..."
sudo apt-get update
echo 20 > /tmp/dependancy_googlecast_in_progress
echo "-- Installation of python3 if not already installed"
sudo apt-get install -y python3 python-dev build-essential
echo 50 > /tmp/dependancy_googlecast_in_progress
echo "-- Installation of pip for python3 and necessary libraries"
sudo apt-get install -y python-requests python3-pip
echo 75 > /tmp/dependancy_googlecast_in_progress
# get pip3 command (different depending of os such as for raspberry)
pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ !  -z  $pip3cmd  ]]; then     # pip3 found
    echo "-- Installation of python library 'requests' with command $pip3cmd"
    $(sudo $pip3cmd install requests>=2.0)
    echo 83 > /tmp/dependancy_googlecast_in_progress
    echo "-- Installation of python library 'protobuf' with command $pip3cmd"
    $(sudo $pip3cmd install protobuf>=3.0.0)
    echo 95 > /tmp/dependancy_googlecast_in_progress
    echo "-- Installation of python library 'zeroconf' with command $pip3cmd"
    $(sudo $pip3cmd install zeroconf>=0.17.7)
    echo 100 > /tmp/dependancy_googlecast_in_progress
    echo "Everything is successfully installed!"
else
    echo 100 > /tmp/dependancy_googlecast_in_progress
    echo "Error: Cound not found pip3 program to install python dependencies !"
fi
sleep 2
rm /tmp/dependancy_googlecast_in_progress
