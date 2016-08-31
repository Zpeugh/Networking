#!/usr/bin/env python3

import sys
import os
import filecmp

OUTPUT_DIR = "recv"
MAX_BYTES = 1000

try:
    file_name = sys.argv[1]
except IndexError as e:
    print("You must input a filename to copy as the first argument")
    sys.exit()

# check if the recv directory exists, create it if it does not
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

# open the new file in the recv directory
try:
    new_file = open(OUTPUT_DIR + "/" + file_name, 'wb')
except IOError as e:
    print("Error creating file in " + OUTPUT_DIR + ":" + e)

# open and read the input file 1000 bytes at a time the and then append
# each data to the output file
try:
    with open(file_name, 'rb') as file_to_copy:
        data = file_to_copy.read(MAX_BYTES)
        while data:
            new_file.write(data)
            data = file_to_copy.read(MAX_BYTES)

    new_file.close()
except IOError as e:
    print("Error opening file with name '" + file_name + "'")
    new_file.close()
    os.remove(new_file.name)
