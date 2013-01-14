##########################################
#unpacking lists of tuples
#mylist = [('foo', 'foo1'), ('bar', 'bar2'), ('baz', 'baz2')]
#for idx, val in mylist:
#    print idx, val

##########################################
#more unpacking
# categories_dict = { 1: ('Business', 'business'),
#     2: ('Bridal', 'bridal'),
#     3: ('Food', 'food'),
#     4: ('Home & Garden', 'home-garden'),
#     5: ('Specials', 'specials'),
#     6: ('Sport and Leisure', 'sport-leisure'),
# }

# for cat_key in categories_dict:
#     # name, slug = *categories_dict[cat_key]
#     # print name, slug
#     name = categories_dict[cat_key]
#     print name

######################################
# slicing is out-of-bounds safe
#mylist = ['foo', 'bar', 'baz']
#get = mylist[len(mylist):10]
#print get

# appending a list
#bats = ['foo', 'bar', 'baz']
#bats[len(bats):] = ['foo', 'bar', 'baz']
#print bats

#adding lists
#foo = [1, 2, 3]
#bar = [4, 5, 6]
#baz = foo + bar
#print baz

# reference the last element of a list
#bats = ['foo', 'bar', 'baz']
#print bats[-1]

# assinging multiple objects
# def assign():
#     foo = 'foo'
#     bar = 'false'

#     bux, qag = (foo, bar) if True else ("nup", "nup")
#     print bux,',', qag

# assign()




#################### SLICING
# a = ['foo', 'bar', 'baz']
# start = 1
# end = 1
# step = 1

# a[start:end] # items start through end-1
# a[start:]    # items start through the rest of the array
# a[:end]      # items from the beginning through end-1
# a[:]         # a copy of the whole array

#There is also the step value, which can be used with any of the above:

#a[start:end:step] # start through not past end, by step

#The key point to remember is that the :end value represents the first value that is not in the selected slice.
#So, the difference beween end and start is the number of elements selected (if step is 1, the default).

#The other feature is that start or end may be a negative number, which means it counts from the end of
#the array instead of the beginning. So:

# a[-1]    # last item in the array
# a[-2:]   # last two items in the array
# a[:-2]   # everything except the last two items

#and a[::-1] to reverse a string.

#Python is kind to the programmer if there are fewer items than you ask for. For example, if you ask for a[:-2]
#and a only contains one element, you get an empty list instead of an error. Sometimes you would prefer the error, so you have to be aware that this may happen.


#names = ['Mark', 'Mark Sievers', 'Mark Daniel Sievers', 'Mr Mark Daniel Sievers']

#for name in names:
#    parts = name.split(' ')
#    first = [:]


################### ENUMERATE
# http://docs.python.org/2/tutorial/datastructures.html#looping-techniques
# convenient way to maintain the loop counter in a for loop]]
#for i, v in enumerate(['tic', 'tac', 'toe']):
#    print i, v

