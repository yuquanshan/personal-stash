from __future__ import print_function

import calendar
import hashlib
import json
import os
import re
import sets
import time

'''
let ada remember either a file, a string and peek the remembered content
for peek, ada will print LINE_BUFFER_SIZE lines above N_MORE_LINES_TO_PRINT lines below
around the regex keyword (case insensitive);
if no keyword provided, ada will show all the content

layout of config:
{file_alias0: file_path0, file_alias1: file_path1, ...}
'''
GREEN_CODE = u"\033[0;32m"
RED_CODE = u"\033[0;31m"
RESET_CODE = u"\033[0;0m"

START_LINE = ">>>>>>>>>>>>>>>>>>>>>>>>>>"
END_LINE = "<<<<<<<<<<<<<<<<<<<<<<<<<<"

LINE_BUFFER_SIZE = 10
N_MORE_LINES_TO_PRINT = 10

# default TTL is 15 days
DEFAULT_TTL = 15
DAY_SECONDS = 3600 * 24

CONFIG_PATH = os.path.expanduser('~/.adaconfig/.config')
MEMORY_PATH = os.path.expanduser('~/.adaconfig/.memory')

def process_memory(*args):
    try:
        # check if the config dir exists
        if os.path.exists(CONFIG_PATH):
            # load config json
            fp = open(CONFIG_PATH, 'r')
            config = json.load(fp)
            fp.close()
        else:
            os.makedirs(os.path.expanduser('~/.adaconfig'))
            fp = open(MEMORY_PATH, 'w')
            fp.close()
            # initilize the config json
            config = {"_memory": MEMORY_PATH}

        if 'peek' in args:
            idx = args.index('peek')
            peek(config, *args[idx + 1:])
        elif 'remember' in args:
            idx = args.index('remember')
            if idx >= len(args) - 1:
                print('remember what?')
                return
            if idx == len(args) - 2:
                remember(config, args[idx + 1])
            else:
                remember(config, args[idx + 1], int(args[-1]))
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
            if args[idx + 1] in config:
                config.pop(args[idx + 1], None)
            else:
                # try deleting hash in _memory
                for hash in args[idx + 1:]:
                    forget(config, hash)
        elif 'config' in args:
            print(config)
        else:
            print("I don't understand the input" + ' '.join(args))
            return
        # flush the config, return
        fp = open(CONFIG_PATH, 'w')
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
        if os.path.exists(config['_memory']):
            with open(config['_memory'], 'r') as fp:
                entries = json.load(fp)
            MEMFORMAT = unicode(GREEN_CODE + "[{} {}] " + RESET_CODE + "{} " + RED_CODE + "(expires in {} hrs)" + RESET_CODE)
            for entry in entries:
                if isinstance(entry, unicode):
                    print(MEMFORMAT.format("UNKNOWN", "UNKNOWN", entry, "UNKNOWN"))
                else:
                    ts = time.localtime(entry[0])
                    time_str = "{}-{}-{} {}:{}:{}".format(
                        ts.tm_year,
                        str(ts.tm_mon).rjust(2, '0'),
                        str(ts.tm_mday).rjust(2, '0'),
                        str(ts.tm_hour).rjust(2, '0'),
                        str(ts.tm_min).rjust(2, '0'),
                        str(ts.tm_sec).rjust(2, '0'))
                    now = calendar.timegm(time.gmtime())
                    if entry[3] * DAY_SECONDS - (now - entry[0]) > 0:
                        print(MEMFORMAT.format(time_str, entry[2], entry[1], "{:.2f}".format((entry[3] * DAY_SECONDS - (now - entry[0])) / 3600.0)))
    # case 2 or 3
    elif args[0] in config or os.path.exists(os.path.expanduser(args[0])):
        # case 2
        if len(args) == 1:
            with open(config[args[0]] if args[0] in config else os.path.expanduser(args[0]), 'r') as fp:
                print(fp.read(), end="")
        # case 3
        else:
            with open(config[args[0]] if args[0] in config else os.path.expanduser(args[0]), 'r') as fp:
                pattern = u".*{}.*".format(args[1].decode('utf8')).lower()
                print(RED_CODE + u"SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
                lines = fp.readlines()
                print_match(lines, pattern)
    # case 4
    else:
        with open(config['_memory'], 'r') as fp:
            pattern = u".*{}.*".format(args[0].decode('utf8')).lower()
            print(RED_CODE + u"SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
            entries = json.load(fp)
        lines = []
        for entry in entries:
            if isinstance(entry, unicode):
                lines.append(entry + '\n')
            else:
                lines.append(entry[1] + '\n')
        print_match(lines, pattern)


def remember(config, s, ttl = DEFAULT_TTL):
    entries = []
    if os.path.exists(config['_memory']):
        with open(config['_memory'], 'r') as f:
            if len(f.read()) > 0:
                f.seek(0)
                entries = json.load(f)
    now = calendar.timegm(time.gmtime())
    buffered_entries = []
    hash = hashlib.sha224(s).hexdigest()[:6]
    hash_set = sets.Set()
    for entry in entries:
        '''
        backward compatibility: the original entries just a list of unicodes
        but in the newest design, i want to make it a list of [ts, str,
        hash(str), ttl (days)] tuples. so if the old format is detected,
        replace it with the new format with default values filled
        '''
        if isinstance(entry, unicode):
            h = hashlib.sha224(entry).hexdigest()[:6]
            hash_set.add(h)
            if hash in hash_set:
                print("WARNING: hash collides with an exising content, replace it with the new one")
                continue
            buffered_entries.append([now, entry, h, DEFAULT_TTL])
        else:
            tdelta = now - entry[0]
            if tdelta > entry[3] * DAY_SECONDS:
                # ttl passed, forget this entry
                continue
            else:
                hash_set.add(entry[2])
                if hash in hash_set:
                    print("WARNING: hash collides with an exising content, replace it with the new one")
                    continue
                buffered_entries.append(entry)
    buffered_entries.append([now, s, hash, ttl])
    with open(config['_memory'], 'w') as f:
        json.dump(buffered_entries, f)


# forget a _memory entry in hash
def forget(config, hash):
    entries = []
    if os.path.exists(config['_memory']):
        with open(config['_memory'], 'r') as f:
            if len(f.read()) > 0:
                f.seek(0)
                entries = json.load(f)
    buffered_entries = []
    for entry in entries:
        ety = entry
        if isinstance(entry, unicode):
            now = calendar.timegm(time.gmtime())
            h = hashlib.sha224(entry).hexdigest()[:6]
            ety = [now, entry, h, DEFAULT_TTL]
        else:
            ety = entry
        if ety[2] == hash:
            # if hash matches, forget by not adding to buffered_entries
            continue
        else:
            buffered_entries.append(ety)
    with open(config['_memory'], 'w') as f:
        json.dump(buffered_entries, f)


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
        l = l.decode('utf8')
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
                print(END_LINE + u"(line: {})".format(line_count))
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
        print(END_LINE + u"(line: {})".format(line_count))
