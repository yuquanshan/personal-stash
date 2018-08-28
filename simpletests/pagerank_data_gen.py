#!/usr/bin/python

import random
import sys

def main_func(start, end, filename, nurls = 400000):
    fi = open(filename, 'w')
    prefix = "www."
    suffix = ".com"
    for i in range(start, end):
        if i % 5000 == 0 and i != 0:
            sys.stdout.write("=")
            sys.stdout.flush()
        edges = random.randint(0, 50)
        population = range(nurls)
        population.remove(i)
        dests = random.sample(population, edges)
        for d in dests:
            tmps = ""
            tmps = (prefix + str(i) + suffix + ' ' + prefix
                + str(d) + suffix + '\n')
            fi.write(tmps)
    fi.close()

if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("usage: pagerank_data_gen.py <start> <end> <filename>"
            + " [pool_size]")
    else:
        if (len(sys.argv) == 4):
            main_func(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
        else:
            main_func(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
