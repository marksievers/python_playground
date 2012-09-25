import re

def find_in(string):
    words = ['foo', 'bar']
    if any(i in mystring for i in words):
        print found
        
def address(address_data):
    non_cities = [' street', ' st', ' road', ' rd', ' avenue', ' ave',  ' mail centre', ' mail center', 'state highway ', ' place', ' square', ' terrace', ' private bag ', 'po box ']
    if 'address_2' in address_data:
        print "address_2 hit!"
    if 'city' not in address_data:
        print "city hit!"
    if re.search(r'^[^0-9]+$', address_data['address_2'], re.I):
        print "regex hit!"    
    if all(i not in address_data['address_2'].lower() for i in non_cities):
        print "non city hit!"   

def e164_numbers():
    numbers = ('0274 784087', '09 4146687', '21513351', '00643 328 8296', '+64 21 974 573', '44734347')

    #our goal here is to conform to the E.164 standard
    #http://en.wikipedia.org/wiki/E.164

    #strip non numeric
    #number = re.sub("[^0-9]", "", number)
    for number in numbers:
        orig = number
        number = re.sub("[^0-9]", "", number)

        #remove international call prefix
        if number[:2] == "00":
            number = number[2:]

        #handle melformed new zealand numbers
        if number[:2] != "64" and len(number) < 12:
            if number[0] == "0":
                number = "64" + number[1:]
            elif len(number) == 7:
                #now we are going to assume they are aucklanders
                number = "649" + number 

        print "Converted %s to %s" % (orig, number)


def test_strip(foo):
    print foo.lstrip('$')

def compare(foo, bar):
    if bar and foo not in bar:
        print "foo is not in bar"
    else:
        print "foo is indeed in bar"

#print '.'.join(['foo', 'quz', 'baz'])
#print ''.join(['exists', 'new'])

#test_strip('$1.50')
#address({'address_2': "Shortland Street"})

#compare(None, " ")

e164_numbers()
