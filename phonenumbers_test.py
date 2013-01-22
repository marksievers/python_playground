#https://github.com/daviddrysdale/python-phonenumbers

import phonenumbers
from phonenumbers.geocoder import area_description_for_number

#FIXED_LINE = 0
#MOBILE = 1
#FIXED_LINE_OR_MOBILE = 2

def do(x):
    phonenumber = phonenumbers.parse(x, 'NZ')
    print "Raw: %s" % x
    print "PhoneNumber: %s" % phonenumber
    print "National: %s" % phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.NATIONAL)
    print "International: %s" % phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    print "E164: %s" % phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.E164)
    print "Possible Number: %s" % phonenumbers.is_valid_number(phonenumber)
    print "Valid Number: %s" % phonenumbers.is_possible_number(phonenumber)
    print "Type: %s" % phonenumbers.number_type(phonenumber)

    print "*********************"
    print '\n'


#do('095515700')
do('5515700')
#do('+6421 025 05196')
#do('021-025 0519')
#do('(021) 025 025')

print dir(phonenumbers)