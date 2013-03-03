def test_conditional(foo):
    if foo is ('qux', 'sux'):
        print 'tuple works'

    if foo is 'foo' or 'bar':
        print 'or works'

#print "result of foo is"
#test_conditional('foo')
#print "Result of qux is"
#test_conditional('qux')

def test_defaultVals():
    if {}:
        print "empty dict"
    if 0:
        print "0"
    if 0.00:
        print "0.00"
    if 1:
        print "1"
    if -1:
        print "-1"
    if []:
        print "empty list"
    if "":
        print "empty string"
#test_defaultVals()

def test_bool_built_in():
    none_string = None
    empty_string = ''
    valid_string = 'foo'

    for foo in (none_string, empty_string, valid_string):
        print foo, 'evaluates to', bool(foo)
#test_bool_built_in()

def a_function_that_throws():
    print "Dodgy function being called"
    fo = None
    fo.list()

def test_turnary():
    to_print = a_function_that_throws() if False else "Nup"
    print test_turnary
#test_turnary()


def test_init(val):
    foo = val or "default"
    print foo
#test_init("Foo")

#http://stackoverflow.com/questions/4841782/python-constructor-and-default-value
def test_unsafe(wordList=None):
    verbose = wordList if wordList is not None else []
    compact = wordList or []

    return (verbose, compact)

#print test_unsafe(None)
#print test_unsafe([])
#print test_unsafe(['foo'])
#print test_unsafe('foo')

def test_effcient_eval(foo, bar, baz):
    if foo and not bar and baz:
        print "Im in!"


#test_effcient_eval(True, True, True)

def return_one_and_two():
    return "one", "two"

#one, two = return_one_and_two()
#print one, two

def plus_equals():
    foo = {'bar': 0, 'baz': 1}
    for k in foo:
        foo[k] += 1
        print k, ' is ', foo[k]
#plus_equals()

def for_loop_counter():
    alist = ['foo', 'bar', 'baz']

    for count, item in enumerate(alist):
        print '{0}. {1}'.format(count, item)
#for_loop_counter()





