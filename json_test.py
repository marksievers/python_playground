import json

json_string = u'{ "id":"mark@foo.com" }'
obj = json.loads(json_string)

print obj