#!/bin/bash

for (( c=1; c<=50; c++ ))
  do
    ./bin/spark-submit --class org.apache.spark.examples.JavaWordCount --master mesos://172.31.16.219:5050 --deploy-mode client --supervise --executor-memory 3000m --total-executor-cores 64 --conf spark.executor.cores=1 --conf spark.mesos.role=wc --conf spark.driver.memory=2500m --conf spark.driver.cores=1 hdfs://172.31.16.219:54310/user/spark-examples_2.11-2.3.0-SNAPSHOT.jar hdfs://172.31.16.219:54310/user/bigtext.txt 1>/dev/null 2>/dev/null
  done

