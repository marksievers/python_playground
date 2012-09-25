import json, sys

#class ValidationResult():
#    def __init__(self, passed=True, messages=None, stop=False):
#        self.passed = passed
#        self.messages = messages
#        self.stop = stop
#
#foo = ValidationResult(messages=['Foo default'], passed=False, stop=False)
#bar = ValidationResult(messages=['Bar default'], passed=True, stop=True)
#foo.messages.append("Foos message")
#
#print foo.messages, foo.passed, foo.stop
#print bar.messages, bar.passed, bar.stop

class A(object):
    def __init__(self, names=None):
        self.names = names
    def print_names(self):
        for n in self.names:
            print n

class B(A):
    def __init__(self):
        super(B, self).__init__(['foo', 'bar'])

myb = B()
myb.print_names()
