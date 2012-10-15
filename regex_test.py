import re

def search(string):
    result = re.search(r'^RD\s?\d+$', string, re.I)
    print result

def contains_no_digits(string):
    print "Operating on", string
    expressions = [r'^[^0-9]+$', r'^[^\d]+$']

    for expression in expressions:
        result = re.search(expression, string, re.I)
        match = True if result else False
        print "%s match for %s" % (match, expression)

def run_engine(string, expressions):
    print "Operating on '%s'" % string

    for expression in expressions:
        result = re.search(expression, string, re.I)
        match = True if result else False
        print "%s match for %s" % (match, expression)

def match_issue(string):
    #issue_re = re.compile(r'^\ *#(\d+)\W+([\w/]+)\D+(\d+)\ *$')
    issue_re = re.compile(r' *# *')
    issue_num_match = issue_re.search(string)
    #issue_num_match.group(1)
    if issue_num_match:
        print "match!"

def match_float(float_str):
    matcher = re.compile(r'^\d+\.\d+$')
    result = matcher.search(float_str)
    if result:
        print 'Match for float: ', float_str, " with ", '^\d+\.\d$'
    else:
        print 'No match for float: ', float_str, " with ", '^\d+\.\d$'

def postcode(string):
    postcode = re.search(r'[^(unit|box|po box|private bag)][^\s]*\s{2}(\d{3,})$', string, re.I)
    #postcode = re.search(r'.*\s{2}(\d{3,})$', string, re.I)

    if postcode:
        print "Its a match"


#run_engine("33333", [r'^[\d]$'])
#run_engine("  ", [r'^[\s]$'])
#run_engine("44.00", [r'^[\s]$'])
#postcode("Navarra  31007")
postcode("Navarra  31007")
#postcode("  31007")