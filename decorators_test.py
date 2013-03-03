#decorators http://stackoverflow.com/questions/739654/understanding-python-decorators#1594484

from functools import wraps

###################
#Test decorating
#http://www.artima.com/weblogs/viewpost.jsp?thread=240845
###################

class entryExit(object):

    def __init__(self, f):
        self.f = f

    def __call__(self):
        print "Entering", self.f.__name__
        self.f()
        print "Exited", self.f.__name__

@entryExit
def func1():
    print "inside func1()"

@entryExit
def func2():
    print "inside func2()"

#func1()
#func2()

##################
#test decorating without args using wraps
##################

def _validator(wrapped_function):
    @wraps(wrapped_function)
    def _decorator(*args, **kwargs):
        print "It's good", args, kwargs
        return wrapped_function(*args, **kwargs)
    return _decorator

@_validator
def a_simple_func(foo):
    print foo, "hi"

a_simple_func('bar')
###################
#Test decorating with arguments
#http://www.artima.com/weblogs/viewpost.jsp?thread=240845
###################

class MyForm:
    def __init__(self, form_string='A Default Form'):
        self.form_string = form_string

    def validate(self):
        return True if self.form_string else False

def validate_form(form_class=None):
    def _validator(user_post_function):
        @wraps(user_post_function)
        def _decorator(*args, **kwargs):
            form = form_class(*args, **kwargs)

            if not form.validate():
                print  'Failed to validate'
                return

            return user_post_function(form.form_string)
        return _decorator
    return _validator

@validate_form(MyForm)
def user_post(data):
    print data

#user_post(None)
#user_post('foo')