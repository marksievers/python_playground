

def overload(string_one, string_two):
    print 'overload(string_one, string_two)'


def overload(other_one, other_two):
    print 'overload(string_one, string_two)'

def overload(int):
    print 'overload(int)'


#breaks
overload(string_one='foo', string_two='bar')