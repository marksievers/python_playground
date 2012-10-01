from functools import wraps

###################
#Test wrapping
###################

class MyForm:
    def __init__(self, form_string='A Default Form'):
        self.form_string = form_string

    def validate(self):
        return True if self.form_string else False

def validate_form(form_class=None):
    def _validator(f):
        @wraps(f)
        def _decorator(*args, **kwargs):
            form = form_class(*args, **kwargs)
            
            if not form.validate():
                print  'Failed to validate'
                return
            
            return f(form.form_string)
        return _decorator
    return _validator

@validate_form(MyForm)
def user_post(data):
    print data

user_post(None)
user_post('foo')

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












