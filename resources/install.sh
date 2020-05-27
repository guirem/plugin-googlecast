#!/bin/bash
touch /tmp/dependancy_googlecast_in_progress
echo 0 > /tmp/dependancy_googlecast_in_progress
echo "Launch install of googlecast dependancies"
echo ""
export DEBIAN_FRONTEND=noninteractive
echo "-- Current OS version :"
sudo lsb_release -d
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
pyver=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\+\).*/\1\2/')
if [ "$pyver" -lt "35" ]; then  # using 3.4 that is depreciated
    echo "  Your version of python is not compatible with this plugin, installation might not work correctly !"
else
    echo "  Your version of python is compatible with this plugin."
fi
echo 50 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of pip for python3 and necessary libraries"
sudo apt-get install -y python3-dev python-requests python3-pip
echo 68 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of audio sox library"
sudo apt-get install -y sox
echo 71 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of TTS libraries"
sudo apt-get install -y libttspico-utils
echo 73 > /tmp/dependancy_googlecast_in_progress
echo ""
echo "-- Installation of libav/ffmpeg libraries"
if [ $(sudo apt-cache search --names-only '^ffmpeg$' | wc -l) -eq 1 ]; then
    sudo apt-get install -y ffmpeg
else
    sudo apt-get install -y libav-tools libavcodec-extra
fi
echo 75 > /tmp/dependancy_googlecast_in_progress
# get pip3 command (different depending of OS such as raspberry)
pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ -z  $pip3cmd ]]; then     # pip3 not found
    if python3 -m pip -V 2>&1 | grep -q -i "^pip " ; then     # but try other way
        pip3cmd="python3 -m pip"
    else # something is wrong with pip3 so reinstall it
        echo "-- Something is wrong with pip3, trying to re-install :"
        sudo python3 -m pip uninstall -y pip
        sudo apt-get -y --reinstall install python3-pip
        pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
    fi
fi
if [[ ! -z  $pip3cmd ]]; then     # pip3 found
    echo ""
    echo "-- Upgrade setuptools with command $pip3cmd if not up to date"
    if [ "$pyver" -lt "35" ]; then  # using 3.4 that is depreciated
        $(sudo $pip3cmd install setuptools > /tmp/dependancy_googlecast)
    else
        $(sudo $pip3cmd install 'setuptools>=42.0.0' > /tmp/dependancy_googlecast)
    fi
    cat /tmp/dependancy_googlecast
    echo 78 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installed version of pip :"
    echo $($pip3cmd -V)
    echo ""
    #echo "-- Installation of python library 'netifaces' with command $pip3cmd"
    #$(sudo $pip3cmd install netifaces > /tmp/dependancy_googlecast)
    #cat /tmp/dependancy_googlecast
    #echo 80 > /tmp/dependancy_googlecast_in_progress
    #echo ""
    echo "-- Installation of python library 'requests' with command $pip3cmd"
    if [ "$pyver" -lt "35" ]; then  # using 3.4 that is depreciated
        $(sudo $pip3cmd install 'requests' > /tmp/dependancy_googlecast)
    else
        $(sudo $pip3cmd install 'requests>=2.21.0' > /tmp/dependancy_googlecast)
    fi
    cat /tmp/dependancy_googlecast
    echo 83 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'protobuf' with command $pip3cmd"
    if [ "$pyver" -lt "35" ]; then  # using 3.4 that is depreciated
        $(sudo $pip3cmd install 'protobuf' > /tmp/dependancy_googlecast)
    else
        $(sudo $pip3cmd install 'protobuf>=3.11.0' > /tmp/dependancy_googlecast)
    fi
    cat /tmp/dependancy_googlecast
    echo 87 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'zeroconf' with command $pip3cmd"
    $(sudo $pip3cmd install 'zeroconf>=0.25.1' > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 92 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'click, bs4 and six' for TTS with command $pip3cmd"
    $(sudo $pip3cmd install click bs4 six > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 96 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of python library 'tqdm, websocket-client, casttube' for plex/youtube with command $pip3cmd"
    $(sudo $pip3cmd install tqdm websocket-client casttube > /tmp/dependancy_googlecast)
    cat /tmp/dependancy_googlecast
    echo 100 > /tmp/dependancy_googlecast_in_progress
    echo ""
    echo "-- Installation of dependencies is done !"
    rm -f /tmp/dependancy_googlecast
else
    echo ""
    echo "Error: Cound not found pip3 program to install python dependencies ! Check doc FAQ for possible resolution."
fi
echo 100 > /tmp/dependancy_googlecast_in_progress
rm /tmp/dependancy_googlecast_in_progress
