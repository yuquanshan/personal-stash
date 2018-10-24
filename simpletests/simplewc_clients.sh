#!/bin/bash

for (( c=1; c<=50; c++ ))
  do
    echo "Doing $c..."
    /home/ubuntu/psuspark/spark-2.4.0-SNAPSHOT-bin-custom-spark/bin/spark-submit --class SimpleWC --master mesos://172.31.94.221:5050 --deploy-mode client --supervise --conf spark.network.timeout=1800s --conf spark.debug.fudge=0.0 --conf spark.debug.arf=0.3 hdfs://172.31.28.117:54310/simplewc_2.11-1.0.jar $c 0 1>>simplewcoptmulti.out 2>>simplewcoptmulti.err
  done
