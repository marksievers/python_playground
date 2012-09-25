import httplib
import simplejson as json

http.HttpConnection.request

conn = httplib.HTTPConnection("api.wenzani.com")
conn.request("GET", "/experience/search/guest?user_ids=13699")
response = conn.getresponse()
print response.status, 'and', response.reason
conn.close()

#loads = json.loads()
#loads = json.loads(data1)
#print loads[0]
