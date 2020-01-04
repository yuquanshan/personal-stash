from __future__ import print_function

import json
import os
import re

'''
let ada remember either a file, a string and peek the remembered content
for peek, ada will print LINE_BUFFER_SIZE lines above N_MORE_LINES_TO_PRINT lines below
around the regex keyword (case insensitive);
if no keyword provided, ada will show all the content
string memory is a FIFO queue whose capacity is _mem_cap defined in config
'''
GREEN_CODE = "\033[0;32m"
RED_CODE = "\033[0;31m"
RESET_CODE = "\033[0;0m"

START_LINE = ">>>>>>>>>>>>>>>>>>>>>>>>>>"
END_LINE = "<<<<<<<<<<<<<<<<<<<<<<<<<<"

LINE_BUFFER_SIZE = 10
N_MORE_LINES_TO_PRINT = 10

def process_memory(*args):
    try:
        # check if the config dir exists
        if os.path.exists(os.path.expanduser('~/.adaconfig/.config')):
            # load config json
            fp = open(os.path.expanduser('~/.adaconfig/.config'), 'r')
            config = json.load(fp)
            fp.close()
        else:
            os.makedirs(os.path.expanduser('~/.adaconfig'))
            fp = open(os.path.expanduser('~/.adaconfig/.memory'), 'w')
            fp.close()
            # initilize the config json
            config = {"_mem_cap": 5}

        if 'peek' in args:
            idx = args.index('peek')
            peek(config, *args[idx + 1:])
        elif 'remember' in args:
            idx = args.index('remember')
            if idx >= len(args) - 1:
                print('remember what?')
                return
            remember(config, args[idx + 1])
        elif 'register' in args:
            idx = args.index('register')
            if idx + 2 > len(args) - 1:
                print('to register, specify <alias> <file_path>')
                return
            register(config, args[idx + 1], args[idx + 2])
        elif 'forget' in args:
            idx = args.index('forget')
            if idx >= len(args) - 1:
                print('forget what?')
                return
            config.pop(args[idx + 1], None)
        else:
            print("I don't understand the input" + ' '.join(args))
            return
        # flush the config, return
        fp = open(os.path.expanduser('~/.adaconfig/.config'), 'w')
        json.dump(config, fp)
    except Exception as e:
        print(e)


'''
args can be:
1. <empty>: showing all memory
2. [<alias/file>]: showing all content in alias/file
3. [<alias/file> <regex>]: showing the adjacent lines around regex matches
4. [<regex>]: showing all memory that matches regex
'''
def peek(config, *args):
    # case 1
    if len(args) == 0:
        if os.path.exists(os.path.expanduser(os.path.expanduser('~/.adaconfig/.memory'))):
            with open(os.path.expanduser('~/.adaconfig/.memory'), 'r') as fp:
                lines = json.load(fp)
                for l in lines:
                    print(l)
    # case 2 or 3
    elif args[0] in config or os.path.exists(os.path.expanduser(args[0])):
        # case 2
        if len(args) == 1:
            with open(config[args[0]] if args[0] in config else os.path.expanduser(args[0]), 'r') as fp:
                print(fp.read(), end="")
        # case 3
        else:
            with open(config[args[0]] if args[0] in config else os.path.expanduser(args[0]), 'r') as fp:
                pattern = ".*{}.*".format(args[1]).lower()
                print(RED_CODE + "SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
                lines = fp.readlines()
                print_match(lines, pattern)
    # case 4
    else:
        with open(os.path.expanduser('~/.adaconfig/.memory'), 'r') as fp:
            pattern = ".*{}.*".format(args[0]).lower()
            print(RED_CODE + "SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
            lines = json.load(fp)
            lines = [l + '\n' for l in lines]
            print_match(lines, pattern)


def remember(config, s):
    config["_memory"] = os.path.expanduser('~/.adaconfig/.memory')
    lines = []
    if os.path.exists(os.path.expanduser('~/.adaconfig/.memory')):
        with open(os.path.expanduser('~/.adaconfig/.memory'), 'r') as f:
            if len(f.read()) > 0:
                f.seek(0)
                lines = json.load(f)
        if len(lines) >= config['_mem_cap']:
            lines = lines[len(lines) - config['_mem_cap'] + 1]
    lines.append(s)
    with open(os.path.expanduser('~/.adaconfig/.memory'), 'w') as f:
        json.dump(lines, f)


def register(config, alias, fp):
    if not os.path.exists(os.path.expanduser(fp)):
        raise Exception("File " + fp + " doesn't exist")
    config[alias] = fp


def print_match(lines, pattern):
    line_buffer = []
    match_in_buffer = False
    more_lines_countdown = 0
    line_count = 0
    for l in lines:
        line_count = line_count + 1
        match = re.match(pattern, l.lower())
        if match:
            match_in_buffer = True
            more_lines_countdown = N_MORE_LINES_TO_PRINT
            line_buffer.append(GREEN_CODE + l + RESET_CODE)
        elif match_in_buffer:
            line_buffer.append(l)
            more_lines_countdown = more_lines_countdown - 1
            if more_lines_countdown == 0:
                print(START_LINE)
                for i in line_buffer:
                    print(i, end="")
                print(END_LINE + "(line: {})".format(line_count))
                line_buffer = line_buffer[-LINE_BUFFER_SIZE:]
                match_in_buffer = False
        else:
            if len(line_buffer) == LINE_BUFFER_SIZE:
                line_buffer.pop(0)
            line_buffer.append(l)
    if match_in_buffer:
        print(START_LINE)
        for i in line_buffer:
            print(i, end="")
        print(END_LINE + "(line: {})".format(line_count))
