#!/usr/bin/env bash
pipenv shell

# Надо запустить асинхроно flask и rq и если один из них вылетел, то другой закрыть
python __init__.py &
PID1=$!

rq worker  --results-ttl 5 &
PID2=$!

while true; do
    if ! kill -0 $PID1 || ! kill -0 $PID2; then
	kill $PID1
	kill $PID2
	exit 1
    fi
    sleep 2

done
