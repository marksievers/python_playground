import datetime
import time

def string_to_datetime(d):
    return datetime.datetime.strptime(d, "%d/%m/%Y")

#print string_to_datetime("02/04/2012")
#print string_to_datetime("")

def get_duration():
    suboff_start = time.time()
    time.sleep(1)
    suboff_end = time.time()
    result = datetime.timedelta(seconds=suboff_end-suboff_start)
    print "%s" % result
    print "%s" % result.seconds
    print "%s" % result.microseconds

#get_duration()

def datetime_to_string(datetime):
    return datetime.strftime("%d-%b-%Y")

print datetime_to_string(datetime.datetime.now())


#date now
#print datetime.datetime.now()

#time now
#print datetime.datetime.time(datetime.datetime.now())


#print "A datetime object ", datetime.datetime.strptime("08/07/2012", "%d/%m/%Y")
#print "A date object ", datetime.date(2012, 7, 8)

#formatting symbols
#http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior



#to and from a unix timestamp
# now = datetime.datetime.now()
# time.mktime(now.timetuple())

# datetime.datetime.fromtimestamp(1314066603)


