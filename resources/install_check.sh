#!/bin/bash
if ! python3 -V 2>&1 | grep -q "Python 3"; then
    echo "nok"
    exit 0
fi

pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ -z  $pip3cmd ]]; then     # pip3 not found
    if python3 -m pip -V 2>&1 | grep -q -i "^pip " ; then     # but try other way
        pip3cmd="python3 -m pip"
    else
        echo "nok"
        exit 0
    fi
fi
if [[ !  -z  $pip3cmd  ]]; then     # pip3 found
    $(sudo $pip3cmd list 2>/dev/null | grep -E "zeroconf|requests|protobuf|bs4|websocket-client|tqdm" | wc -l > /tmp/dependancycheck_googlecast)
    content=$(cat /tmp/dependancycheck_googlecast 2>/dev/null)
    rm -f /tmp/dependancycheck_googlecast
    if [[ -z  $content  ]]; then
        content=0
    fi
    if [ "$content" -lt 7  ];then
        echo "nok"
        exit 0
    fi
else
    echo "nok"
    exit 0
fi
echo "ok"
exit 0
