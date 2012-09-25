import json

def load(json):
    try:
        d = json.loads(json)
        return d
    except:
        print "Fucked!"


def return_tuple():
    foo = 'foo'
    bar = 'bar'
    return foo, bar

#print load('{"foo"}')

foo = return_tuple()
print foo
