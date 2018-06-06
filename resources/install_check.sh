if ! python3 -V 2>&1 | grep -q "Python 3"; then
    echo "nok"
    exit 0
fi

pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ !  -z  $pip3cmd  ]]; then     # pip3 found
    $(sudo $pip3cmd list 2>/dev/null | grep -E "zeroconf|requests|protobuf|netifaces|bs4|websocket-client|tqdm" | wc -l > /tmp/dependancycheck_googlecast)
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
