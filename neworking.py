import json
import urllib2
from urllib2 import HTTPError

try:
    data = json.dumps({
        'email': 'foo@bar.ned',
        'first_name': 'Foo',
        'last_name': 'Bar',
        'password': 'foobar',
    })
    print data
    url = "http://subscriber-api.dev.andsomeideas.com/api/subscriber_post/?format=json"
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response `= f.read()
    f.close()

    print response
except HTTPError as e:
    print e
    print e.read()
