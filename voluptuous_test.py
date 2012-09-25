from voluptuous import Schema, required, Invalid
from voluptuous import coerce as my_coerce
from voluptuous import any as my_any
from voluptuous import all as my_all
from voluptuous import range as my_range

cd = {
        required('title'): str,
        'discs': int,
        'matrix': [str],
        'source': my_all(my_any('pro', 'aud')),
        'producer': str,
        'quality': my_all(my_any('perfect','excellent','average','poor')),
        'generation': my_all(my_any('master','high','medium','low')),
        'duration': my_all(my_coerce(float), float),
        'tracklists': [[str]],
        'date': {
            required('d'): my_all(int, my_range(min=1, max=31)),
            required('m'): my_all(int, my_range(min=1, max=12)),
            required('y'): my_all(int, my_range(min=1981, max=2050))
            }
}
cd_schema = Schema(cd)

#result = cd_schema({
#    'title': "My CD Title",
#    'discs': 2,
#    'matrix': ["cd1_code"],
#    'source': 'pro',
#    'producer': "The Godfather Records",
#    'quality': "perfect",
#    'generation': "high",
#    'duration': 76,
#    'tracklists': [['foo']],
#    'date': {
#        'd': 1,
#        'm': 2,
#        'y': 1983
#        }
#    })
#print result

item_schema = Schema({
    'gig_ids': [int],
    required('tags'): [my_all(str, my_any('cd', 'dvd', 'boxset'))],
    'cds': [cd]
    })
try:
    result = item_schema({
        'gig_ids': [1, 2],
        'tags': ['cd'],
        'unknown_ele': 'ele',
        'cds': [{
            'title': "My CD Title",
            'discs': 2,
            'matrix': ["cd1_code"],
            'source': 'pro',
            'producer': "The Godfather Records",
            'quality': "perfect",
            'generation': "high",
            'duration': 76,
            'tracklists': [['foo']],
            'date': {
                'd': 1,
                'm': 2,
                'y': 1983
                }
            }, {
            'title': "My  second CD Title",
            'discs': 1,
            'matrix': ["cd1_code"],
            'source': 'pro',
            'producer': "The Godfather Records",
            'quality': "perfect",
            'generation': "high",
            'duration': 76,
            'tracklists': [['foo']],
            'date': {
                'd': 1,
                'm': 2,
                'y': 1983
                }
            }]
        })
except Invalid as e:
#except Exception as e:
    print 'failed: ', e.msg, e.path

#print result
