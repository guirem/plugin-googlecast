touch /tmp/dependancy_googlecast_in_progress
echo 0 > /tmp/dependancy_googlecast_in_progress
echo "Launch install of googlecast dependancies"
echo ""
echo "-- Updating repo..."
sudo apt-get update
echo 20 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of python3 and dependancies"
sudo apt-get install -y python3 python-dev build-essential
echo ""
echo "-- Installed version of Python :"
python3 -V
echo 50 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of pip for python3 and necessary libraries"
sudo apt-get install -y python3-dev python-requests python3-pip
echo 70 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of TTS libraries"
sudo apt-get install -y libttspico-utils libavcodec-extra libav-tools sox
echo 75 > /tmp/dependancy_googlecast_in_progress
# get pip3 command (different depending of OS such as raspberry)
pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ !  -z  $pip3cmd  ]]; then     # pip3 found
    echo ""
    echo "-- Installation of python library 'netifaces' with command $pip3cmd"
    $(sudo $pip3cmd install netifaces > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 80 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'requests' with command $pip3cmd"
    $(sudo $pip3cmd install requests>=2.0 > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 83 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'protobuf' with command $pip3cmd"
    $(sudo $pip3cmd install protobuf>=3.0.0 > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 87 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'zeroconf' with command $pip3cmd"
    $(sudo $pip3cmd install zeroconf>=0.17.7 > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 92 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'click, bs4 and six' for TTS with command $pip3cmd"
    $(sudo $pip3cmd install click bs4 six > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 96 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'tqdm, websocket-client' for plex with command $pip3cmd"
    $(sudo $pip3cmd install tqdm websocket-client > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 100 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of dependencies is done !"
    rm -f /tmp/dependancy_googlecast
else
    echo ""
    echo "Error: Cound not found pip3 program to install python dependencies !"
fi
echo 100 > /tmp/dependancy_googlecast_in_progress
rm /tmp/dependancy_googlecast_in_progress
