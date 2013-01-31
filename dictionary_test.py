def list_comprehesions():
    my_dict = {"1": "foo", "2": "bar"}
    messages = [": ".join([x, my_dict[x]]) for x in my_dict]
    print messages

def iterators():
    dictionary = {'1': 'one', '2': 'two', '3': 'there'}
    for key, value in dictionary.items():
        print key, value
        del dictionary[key]
        print "After del: ", dictionary

#iterators()

#test 'not in' syntax
d = {'foo': 'foo value'}
if 'foo' not in d:
    print 'No foos here'

elif not 'foo' in d:
    print 'No foos here either'
