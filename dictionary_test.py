def test_get_method():
    foo = {}
    print foo.get('bar')

test_get_method()

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


def not_in_syntax():
    d = {'foo': 'foo value'}
    if 'foo' not in d:
        print 'No foos here'

    elif not 'foo' in d:
        print 'No foos here either'


def ordered_dict():
    import collections

    data = collections.OrderedDict()
    data['foo'] = 'foo'

    print data

def join_dicts():
    a = {'foo': 'foo value', 'bar': 'bar_value'}
    b = {'qux': 'qux value', 'bar': 'bar_value'}
    c = dict(a.items() + b.items())

    print c

# join_dicts()