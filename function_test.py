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

func1()
func2()

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

####################
#Test dicts
###################
# def myfunc(foo):
#     if foo == 'bar':
#         return 'Success'
#
# def my_dict_func(foo,bar={}):
#     print foo, 'and', bar
#
# print myfunc('bar'), ' and ', myfunc('foo')
#
# my_dict_func('stink')

######################
# Test inheritience
######################

#class ClassA():
#    globalvar= "global"
#
#    def __init__(self):
#        self.color = 'green'
#
#first = ClassA()
#second = ClassA()
#
#print "First.globalvar =", first.globalvar
#print "Second.globalvar =", second.globalvar
#
#first.globalvar = 'new globalvar'
#print "After assignment"
#print "First.globalvar =", first.globalvar
#print "Second.globalvar =", second.globalvar

########################

########################
# Test Named attributes
########################
#def myfunction(foo='foo', bar='bar', qux='qux'):
#    print foo, bar, qux

#myfunction(None)

########################

########################
# Test returning multiple values
#######################

# def returns_three(foo, bar, baz):
#     return foo, bar, baz

# def multiplies_three(foo, bar, baz, qux):
#     return foo*2, bar*2, baz*2, qux*2


# values = returns_three(1, 2 , 3)
# print values

# mutiplied = multiplies_three(10, *values)
# print mutiplied












