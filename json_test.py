import json

json_string = u'{ "id":"123456789" }'
obj = json.loads(json_string)

print obj