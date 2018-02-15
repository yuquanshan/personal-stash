import datetime
import json
import logging
import random
from sets import Set

SCHEDULER_MAP = {"Default": 0, "Selective": 1}
LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.CRITICAL,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
    }

class Simulator:
    class Task:
        def __init__(self, tid):
            self.tid = tid
        def assignTo(self, core, countDown):
            self.core = core
            self.countDown = countDown
            self.duration = countDown
            self.speculated = False

    def __init__(self, conf = "default.conf"):
        fi = open(conf, "r")
        jstr = fi.read()
        fi.close()
        jdata = json.loads(jstr)

        self.cores = int(jdata["cores"]) if jdata.has_key("cores") else 500
        self.crippled_cores_p = float(
            jdata["crippled_cores_p"]) if jdata.has_key(
            "crippled_cores_p") else 0.5
        self.tasks = int(jdata["tasks"]) if jdata.has_key("tasks") else 1000
        self.task_mean = int(jdata["task_mean"]) if jdata.has_key(
            "task_mean") else 60000
        self.task_sigma = int(jdata["task_sigma"]) if jdata.has_key(
            "task_sigma") else 10000
        self.task_slowdown = float(jdata["task_slowdown"]) if jdata.has_key(
            "task_slowdown") else 0.4
        self.speculation = jdata["speculation"] if jdata.has_key(
            "speculation") else False
        self.speculation_interval = int(
            jdata["speculation_interval"]) if jdata.has_key(
            "speculation_interval") else 100
        self.speculation_multiplier = float(
            jdata["speculation_multiplier"]) if jdata.has_key(
            "speculation_multiplier") else 1.5
        self.speculation_quantile = float(
            jdata["speculation_quantile"]) if jdata.has_key(
            "speculation_quantile") else 0.75
        self.scheduler = jdata["scheduler"] if jdata.has_key(
            "scheduler") else "Default"
        self.loglevel = jdata["log_level"] if jdata.has_key(
            "log_level") else "INFO"
        assert self.scheduler in SCHEDULER_MAP, self.scheduler + " not found!"
        assert self.loglevel in LEVEL_MAP, self.loglevel + " not found!"
        logging.basicConfig(format = '%(message)s')
        self.logger = logging.getLogger('Default')
        self.logger.setLevel(LEVEL_MAP[self.loglevel])
        pass


    def run(self):
        self.logger.debug(self.getConfigMsg())
        corelist = range(0, self.cores)
        availableCores = Set(corelist)
        crippledCores = self.randomSelect(corelist,
            int(self.cores * self.crippled_cores_p))
        nextTask = 0
        runningTasks = {}
        timer = 0
        completedTasks = [] # records the durations, forget the task number
        while len(runningTasks) > 0 or nextTask < self.tasks:
            # progress the running tasks
            newrunningTasks = {}
            for tid in runningTasks:
                newrunningTasks[tid] = runningTasks[tid]
                for task in runningTasks[tid]:
                    task.countDown = task.countDown - 1
                    if task.countDown <= 0:
                        self.logger.debug(self.msToTime(timer) + "Task "
                            + str(tid) + " has finished.")
                        completedTasks.append(task.duration)
                        for t in runningTasks[tid]:
                            self.logger.debug(self.msToTime(timer) + "Core "
                                + str(t.core) + " has been released.")
                            availableCores.add(t.core)
                        del newrunningTasks[tid]
                        break
                    else:
                        # can do speculative execution
                        if (self.speculation
                              and timer % self.speculation_interval == 0
                              and len(completedTasks)
                              > int(self.speculation_quantile * self.tasks)):
                            completedTasks.sort()
                            if (task.duration - task.countDown
                                > completedTasks[len(completedTasks)/2]
                                and not task.speculated):
                                tmpcore = self.schedulers()[
                                    SCHEDULER_MAP[self.scheduler]](
                                        availableCores, crippledCores)
                                if tmpcore != None:
                                    task.speculated = True
                                    newtask = self.Task(tid)
                                    if tmpcore not in crippledCores:
                                        dur = self.deriveRunTime(
                                            self.task_mean, self.task_sigma)
                                        self.logger.debug(self.msToTime(timer)
                                            + "Consuming normal core "
                                            + str(tmpcore)
                                            + " for speculating Task "
                                            + str(tid)
                                            + ", will run for " + str(dur)
                                            + " ms.")
                                        newtask.assignTo(tmpcore, dur)  
                                    else:
                                        dur = self.deriveRunTime(
                                            self.task_mean
                                            / self.task_slowdown,
                                            self.task_sigma
                                            / self.task_slowdown)
                                        self.logger.debug(self.msToTime(timer)
                                            + "Consuming slow core "
                                            + str(tmpcore)
                                            + " for speculating Task "
                                            + str(tid)
                                            + ", will run for " + str(dur)
                                            + " ms.")
                                        newtask.assignTo(tmpcore, dur)
                                    newrunningTasks[tid].append(newtask)
            runningTasks = newrunningTasks
            while nextTask < self.tasks:
                tmpcore = self.schedulers()[SCHEDULER_MAP[self.scheduler]](
                    availableCores, crippledCores)
                if tmpcore != None:
                    newtask = self.Task(nextTask)
                    if tmpcore not in crippledCores:
                        dur = self.deriveRunTime(
                            self.task_mean, self.task_sigma)
                        self.logger.debug(self.msToTime(timer)
                            + "Consuming normal core "
                            + str(tmpcore)
                            + " for Task "
                            + str(nextTask)
                            + ", will run for " + str(dur) + " ms.")
                        newtask.assignTo(tmpcore, dur)
                    else:
                        dur = self.deriveRunTime(
                            self.task_mean / self.task_slowdown,
                            self.task_sigma / self.task_slowdown)
                        self.logger.debug(self.msToTime(timer)
                            + "Consuming slow core "
                            + str(tmpcore)
                            + " for Task "
                            + str(nextTask)
                            + ", will run for " + str(dur) + " ms.")
                        newtask.assignTo(tmpcore, dur)
                    runningTasks[nextTask] = [newtask]
                    nextTask = nextTask + 1
                else:
                    break
            # progress the timer
            timer = timer + 1
        self.logger.info("Total run time: " + str(timer) + ' ms.')
        return timer


    def deriveRunTime(self, mu, sigma):
        return int(random.gauss(mu, sigma))


    def default_schedule(self, availablePool, crippledCores):
        # return any one of the availbe slaves
        if len(availablePool) == 0:
            return None
        return availablePool.pop()

    # only choose non-crippled cores
    def selectively_schedule(self, availablePool, crippledCores):
        li = list(availablePool)
        for _core in li:
            if _core not in crippledCores:
                availablePool.remove(_core)
                return _core
        return None


    # randomly select num elems from list l
    def randomSelect(self, l, num):
        assert len(l) >= num
        result = Set()
        while(num > 0):
            tmp = random.randint(0, len(l) - 1)
            result.add(l[tmp])
            del l[tmp]
            num = num -1
        return result


    def msToTime(self, ms):
        """
        s = str(ms / 3600000)
        ms = ms % 3600000
        s = s + ':' + str(ms / 60000)
        ms = ms % 60000
        s = s + ':' + str(ms / 1000) + '.' + str(ms % 1000)
        return s
        """
        return datetime.datetime.fromtimestamp(
            18000.0 + ms/1000.0).strftime('[%H:%M:%S.%f]')

    def schedulers(self):
        return [self.default_schedule, self.selectively_schedule]


    def getConfigMsg(self):
        configmsg = ("{:25s}{}\n".format("Num of cores:", str(self.cores))
                    + "{:25s}{}\n".format("Num of Slow Cores:",
                        str(int(self.cores * self.crippled_cores_p)))
                    + "{:25s}{}\n".format("Num of Tasks:", str(self.tasks))
                    + "{:25s}{}\n".format("Task Duration Mean:",
                        str(self.task_mean))
                    + "{:25s}{}\n".format("Task Duration Sigma:",
                        str(self.task_sigma))
                    + "{:25s}{}\n".format("Task Slowdown:",
                        str(self.task_slowdown))
                    + "{:25s}{}\n".format("Speculation:",
                        str(self.speculation))
                    + "{:25s}{}\n".format("Speculation Interval:",
                        str(self.speculation_interval))
                    + "{:25s}{}\n".format("Speculation Multiplier:",
                        str(self.speculation_multiplier))
                    + "{:25s}{}\n".format("Speculation Multiplier:",
                        str(self.speculation_quantile))
                    + "{:25s}{}\n".format("Scheduler:", self.scheduler)
                    + "{:25s}{}\n".format("Log Level:", self.loglevel))
        return ("==================================================\n"
               + configmsg
               + "==================================================")

if __name__ == "__main__":
    sim = Simulator()
    sim.run()
