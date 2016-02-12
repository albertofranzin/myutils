#!/usr/bin/python

import csv
import fnmatch
import numpy
import os
import re
import subprocess
import sys


def get_file_list(argv):
    argc = len(sys.argv)
    target_dir = argv[1]
    target_extensions = argv[2:]
    file_ext_regex = ""
    for k in range(2,argc):
        file_ext_regex = file_ext_regex + '\|' + argv[k]
    file_ext_regex = file_ext_regex[2:]

    findCMD = 'find ' + target_dir + ' -regex ".*\(' + file_ext_regex + '\)"'
    out = subprocess.Popen(findCMD, shell=True, stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Get standard out and error
    (stdout, stderr) = out.communicate()
     
    # Save found files to list
    filelist = stdout.decode().split()

    return filelist


def python_extract(filename):
    functions = []
    restext = [line.rstrip('\n').lstrip() for line in open(filename)]
    row_indices = [i for i in range(len(restext)) if restext[i].startswith("def ")]
    if len(row_indices) > 0:
        for ri in row_indices:
            functions.extend([restext[ri].split("def ")[1].split("#")[0].split(":")[0].rstrip(' ')])
    return functions


def r_extract(filename):
    functions = []
    restext = [line.rstrip('\n').lstrip() for line in open(filename)]
    row_indices = [i for i in range(len(restext)) if "<- function" in restext[i]]
    if len(row_indices) > 0:
        for ri in row_indices:
            functions.extend([restext[ri].split("<- function")[0].split("#")[0].rstrip(' ')])
    functions = [el for el in functions if el != '']
    return functions


def check_call(filename, functions):
    restext = [line.rstrip('\n').lstrip() for line in open(filename)]
    restext = [restext[i] for i in range(len(restext)) if not restext[i].startswith('#') and not restext[i].startswith('//')]
    restext = ' '.join(restext)
    # print restext
    
    print "\n" + filename + ":"
    for k,v in functions.iteritems():
        if k == filename:
            pass
       #  print k, v
        for val in v:
            if val in restext:
                print "  |-- " + val + " -> " + k

argc = len(sys.argv)
if argc < 3:
    print "\nUsage:\n$ python funcextract.py path/to/project/dir list of file estensions\n"
    sys.exit(1)

filelist = [i for i in get_file_list(sys.argv) if os.path.isfile(i)]

functions = {}

for fileiter in filelist:
    if fileiter.endswith("py"):
        functions[fileiter] = python_extract(fileiter)
    elif fileiter.endswith("R"):
        functions[fileiter] = r_extract(fileiter)

    if len(functions[fileiter]) == 0:
        del functions[fileiter]

print functions


for fileiter in filelist:
    check_call(fileiter, functions)

