def list_comprehesions():
    my_dict = {"1": "foo", "2": "bar"}
    messages = [": ".join([x, my_dict[x]]) for x in my_dict]
    print messages

def iterators():
    dictionary = {'1': 'one', '2': 'two', '3': 'there'}
    for key, value in dictionary.items():
        print key, value
        del dictionary[key]
        print "After del: ", dictionary

iterators()

# 13931, 13965
select * from pg_stat_activity where datname='tangible2012';
select pg_terminate_backend(13931) from pg_stat_activity where datname='tangible2012';