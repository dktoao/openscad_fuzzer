#!/usr/bin/python

# list of files to use as an initial seed
# using the open scad example files example001.scad - example023.scad
file_list = []

for n in range(1,24):
    file_list.append("inputfiles/example{0:03d}.scad".format(n))

# Application to test
app = "/usr/bin/openscad"

# Output fuzz file
fuzzy_file = "fuzzy.scad"

# Test parameters
fuzz_factor = 100
num_tests = 10000

############################## end configuration #############################

import math
import random
import string
import subprocess
import sqlite3

# connect to a database for logging code runs
log_db = sqlite3.connect('openscad_fuzzlog.sqlite')
log_cur = log_db.cursor()

log_cur.execute('''CREATE TABLE IF NOT EXISTS log (
                   id INTEGER PRIMARY KEY,
                   time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   error_code INTEGER,
                   error_msg TEXT,
                   input_file BLOB)''')

log_db.commit()

# outer test loop
for n in range(num_tests):
    file_choice = random.choice(file_list)
    print "Fuzzing run #{0}: {1}".format(n, file_choice)

    buf = bytearray(open(file_choice, 'rb').read())

    # start Charlie Miller code
    num_writes = random.randrange(math.ceil((float(len(buf)) / fuzz_factor)))+1

    for m in range(num_writes):
        rbyte = random.randrange(256)
        rn = random.randrange(len(buf))
        buf[rn] = "%c" % (rbyte)
    # end Charlie Miller code

    open(fuzzy_file, 'wb').write(buf)

    # open process and start logging errors
    process = subprocess.Popen([app, "-o test.stl", fuzzy_file],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err_msg = process.communicate()
    crashed = process.returncode

    # make sure that the error code is valid utf-8
    try:
        err_msg = unicode(err_msg)
    except UnicodeDecodeError:
        err_msg = "Error msg not valid utf-8"

    if crashed < 0:
        log_cur.execute('''INSERT INTO log (error_code, input_file, error_msg)
                           VALUES (?,?,?)''', [crashed, buffer(buf),
                           err_msg.decode('utf-8')])
    else:
        log_cur.execute('''INSERT INTO log (error_code, error_msg)
                           VALUES (?,?)''', [crashed, err_msg.decode('utf-8')])
    if n%100 == 0:
        log_db.commit()

log_db.commit()
