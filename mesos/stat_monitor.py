#!/usr/bin/python

import csv, json, sys, time, urllib2

usage = './stat_monitor.py <config_file>'

def main_func(config_file):
  fi = open(config_file)
  jstr = fi.read()
  fi.close()
  jdata = json.loads(jstr)
  interval = jdata["sampling_interval"]
  span = jdata["monitoring_span"]
  masteraddr = jdata["master_addr"]
  masterurl = "http://" + masteraddr + "/metrics/snapshot"
  monitor(masterurl, interval, span * 60 / interval, jdata["output_path"])

# monitoring: num of completed frameworks, resource (cpu, mem) utilization
# (allocated/total),num of active tasks (executors in coarse-grained Spark)
def monitor(masterurl, interval, num, output):
  num_completed_frameworks = []
  cpu_util = []
  mem_util = []
  num_active_tasks = []
  jstr = urllib2.urlopen(masterurl).read()
  jdata = json.loads(jstr)
  comp_fw_base = jdata["master/messages_unregister_framework"]
  for i in range(0, num):
    time.sleep(interval)
    jstr = urllib2.urlopen(masterurl).read()
    jdata = json.loads(jstr)
    num_completed_frameworks.append(jdata["master/messages_unregister_framework"] - comp_fw_base)
    cpu_util.append(jdata["master/cpus_percent"])
    mem_util.append(jdata["master/mem_percent"])
    num_active_tasks.append(jdata["master/tasks_running"])
  comp_fw_res = ["completed_frameworks"] + num_completed_frameworks
  cpu_util_res = ["cpu_util"] + cpu_util
  mem_util_res = ["mem_util"] + mem_util
  num_tasks_res = ["running_tasks"] + num_active_tasks
  timeline = ["time"] + [interval * x for x in range(1, num + 1)]
  fo = open(output, 'wb')
  owriter = csv.writer(fo)
  owriter.writerow(timeline)
  owriter.writerow(comp_fw_res)
  owriter.writerow(cpu_util_res)
  owriter.writerow(mem_util_res)
  owriter.writerow(num_tasks_res)

if __name__ == "__main__":
  if (len(sys.argv) < 2):
    print usage
  else:
    main_func(sys.argv[1])
