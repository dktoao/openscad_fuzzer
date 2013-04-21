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
fuzz_factor = 250
num_tests = 10

############################## end configuration #############################

import math
import random
import string
import subprocess

# outer test loop
for n in range(num_tests):
    file_choice = random.choice(file_list)

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
    process = subprocess.Popen([app, "-o test{0}.stl".format(n), fuzzy_file])

    crashed = process.wait()

    print crashed
