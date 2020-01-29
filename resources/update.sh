#!/bin/bash

pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ -z  $pip3cmd ]]; then     # pip3 not found
    if python3 -m pip -V 2>&1 | grep -q -i "^pip " ; then     # but try other way
        pip3cmd="python3 -m pip"
fi

if [[ ! -z  $pip3cmd ]]; then     # pip3 found
    echo "-- Updating requirements :"
    echo $($pip3cmd install -r requirements.txt)
else
    echo ""
    echo "Error: Cound not found pip3 program to update python dependencies !"
fi
