rm -f /tmp/dependancycheck_googlecast
if [[ $(python3 -V) != Python* ]]; then
    echo "nok"
    exit 0
fi

pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ !  -z  $pip3cmd  ]]; then     # pip3 found
    $(sudo  $pip3cmd list | grep -E "zeroconf|requests|protobuf" | wc -l > /tmp/dependancycheck_googlecast)

    content=$(cat /tmp/dependancycheck_googlecast)
    if [ "3" == "$content" ];then
        echo "ok"
    else
        echo "nok"
    fi
    rm -f /tmp/dependancycheck_googlecast
    exit 0
else
    echo "nok"
fi
