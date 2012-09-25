import os
import sys
import csv
from os.path import basename
from sys import argv
import re
import time
import datetime
import traceback
import copy

def main():
    
    reader = csv.DictReader(open('csv_test.csv'))
    for row_dict in reader:
        print "Operating on ", row_dict
        for k, v in row_dict.iteritems():
            print k, type(v)

if __name__ == '__main__':
    main()