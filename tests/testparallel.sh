#!/bin/bash

for i in $(seq 1 5); do {
  /bin/bash -c "while true; do lettuce -v 2 -r features/TestExamples.feature; sleep 1; done" & pid=$!
  PID_LIST+=" $pid";
} done

trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";
echo $PID_LIST

wait $PID_LIST

echo
echo "All processes have completed";
