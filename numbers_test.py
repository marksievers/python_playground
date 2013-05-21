decimal_string  = '5.15'

def decimal_format():
    #also rounds
    decimal = 5.1555555
    print "%.2f" % decimal
    rounded = float("%.2f" % decimal)
    print rounded
    print type(rounded)

# decimal_format()

foo = {'foo': 'bar'}

if foo['qux']:
    print 'No qux in here'



def adjusted_prices():
    bundle_price = 100
    offers = [50, 50, 50]

    final_price = 0
    for offer in offers:
        final_price += offer
    modifier = float(bundle_price) / final_price
    print modifier

    incremental_price = 0
    result = {}
    for (index, price) in enumerate(offers):
        result[index] = price * modifier # TODO will need to be rounded to 2 decimal places
        incremental_price += result[index]
        # TODO adjust last item slightly to account for rounding errors

    print result

# adjusted_prices()