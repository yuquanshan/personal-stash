#!/bin/bash

for (( c=1; c<=50; c++ ))
  do
    ./bin/spark-submit --class org.apache.spark.examples.SparkPi --master mesos://172.31.16.219:5050 --deploy-mode client --supervise --executor-memory 1600m --total-executor-cores 128 --conf spark.executor.cores=2 --conf spark.mesos.role=pi --conf spark.driver.memory=1600m --conf spark.driver.cores=1 hdfs://172.31.16.219:54310/user/spark-examples_2.11-2.3.0-SNAPSHOT.jar 11000 1>/dev/null 2>/dev/null
  done

