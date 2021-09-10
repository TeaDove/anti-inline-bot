#!/bin/bash
NAME=$1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

case $2 in
    start)
        kill `cat /var/run/$NAME.pid` 2>/dev/null
        cd $SCRIPT_DIR
        ./start.sh >> out.log 2>&1 & echo $! > /var/run/$NAME.pid;
        ;;
    stop)
        kill `cat /var/run/$NAME.pid` ;;
    *)
        echo "usage: monitor.sh process_name {start|stop}" ;;
esac
exit 0