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

#items = {'fookey':'foovalue','barkey':'barvalue'}
#for item in items:
#    print item

foo = {'foo':'foo_key', 'bar': 'bar_key'}

bar = dict(foo)
bar['new'] = 'new_key'
print bar
