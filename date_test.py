import datetime
import time

def string_to_datetime(d):
    dt = datetime.datetime.strptime(d, "%d/%m/%Y")
    print dt

    return dt

def get_duration():
    suboff_start = time.time()
    time.sleep(1)
    suboff_end = time.time()
    result = datetime.timedelta(seconds=suboff_end-suboff_start)
    print "%s" % result
    print "%s" % result.seconds
    print "%s" % result.microseconds

get_duration()

#print string_to_datetime("02/04/2012")
#print string_to_datetime("")

#print "A datetime object ", datetime.datetime.strptime("08/07/2012", "%d/%m/%Y")
#print "A date object ", datetime.date(2012, 7, 8)
#print "A date object ", datetime.date(2012, 7, 8)