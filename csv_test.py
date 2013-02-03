import os
import sys
import csv
from os.path import basename
from tempfile import TemporaryFile
from sys import argv
import re
import time
import datetime
import traceback
import copy

def main():


    #This works for dirty windows files
    # tf = TemporaryFile('b+wU')
    # for chunk in request.FILES['branch_file'].chunks():
    #   tf.write(chunk)
    # tf.seek(0)
    # csv_reader = reader(tf)


    reader = csv.DictReader(open('APN.csv', 'rU'))
    for row_dict in reader:
        print "Operating on ", row_dict
        for k, v in row_dict.iteritems():
            print k, type(v)

if __name__ == '__main__':
    main()

# http://stackoverflow.com/questions/1875956/how-can-i-access-an-uploaded-file-in-universal-newline-mode
# http://stackoverflow.com/questions/3107793/python-script-reading-from-a-csv-file
# http://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files
# http://docs.python.org/2/library/functions.html#open
# http://selfsolved.com/problems/python-csv-and-universal-newline-mode
# http://docs.python.org/2/library/csv.html#csv-fmt-params
# http://www.gossamer-threads.com/lists/python/dev/723649