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
    if 1:
        print "1"
    if -1:
        print "-1"
    if []:
        print "empty list"
    if "":
        print "empty string"
#test_defaultVals()

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

print test_unsafe(None)
print test_unsafe([])
print test_unsafe(['foo'])
print test_unsafe('foo')




