import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tangible.settings'
sys.path.append('..')
sys.path.append('.')

from django.conf import settings
from django.db import connections
from django.utils.timezone import now
from django.utils.timezone import make_aware

import csv
import re
import time
import datetime
import traceback
import copy
import pprint

from decimal import Decimal
from pytz import timezone
from os.path import basename

from tangy_auth.models import TangyUser
from tangy_subscription.models import Address, Subscription, SentSubscription, Issue, Effort
from tangy_product.models import Product, SubscriptionOffer
from subsplus_resources import au_states, us_state_lookup, nz_cities_and_towns, non_cities

'''
Imports the bulk of subscription data (Users, Addresses, SubOffers, Subscriptions) from the subsplus dumps. Depends on products and issues
so would typically be run after tangible_import.py and provision_issues.py.

This should be run only once (per product) - multiple attempts will result in duplicate data.
'''

#magazine issues, fast lookup
issue_cache = {}
#magazine sub offers, fast lookup
sub_offer_cache = {}
#flagged subs, was imported but needs to be manually verified
flagged_subscriptions = {}

# Address model keys
address_keys = ['address_1', 'address_2', 'city', 'region', 'country', 'postal_code']

#the default effort code
effort = Effort.objects.get(code='initial_migration')

# handles dd/mm/yyyy
def string_to_datetime(d):
    #choose correct year format
    format = "%d/%m/%Y" if len(d.split('/')[2]) == 4 else "%d/%m/%y"
    dt = datetime.datetime.strptime(d, format)
    if dt:
        dt = make_aware(dt, timezone(settings.TIME_ZONE))

    return dt.date()

# TODO clean all strings
def clean_string(candidate):
    cleaned = ''
    if candidate:
        #clean it or use empty string - conform to djangos emprty string preference
        cleaned = candidate.decode('utf-8', 'replace').strip() or cleaned
    return cleaned

def exit(message):
    print message
    sys.exit()

def create_subscriber_address(subscription_row, subscriber, product_code):
    imported_id='%s:%s:sub' % (product_code, subscription_row['Id'])
    try:
        subscriber_address = Address.objects.get(imported_id=imported_id)
    except Address.DoesNotExist:
        subscriber_address = Address(imported_id=imported_id, user=subscriber)

        address_line_1 = clean_string(subscription_row['Address_line_1'])
        address_line_2 = clean_string(subscription_row['Address_line_2'])
        address_line_3 = clean_string(subscription_row['Address_line_3'])
        suburb = clean_string(subscription_row['Suburb'])
        state = clean_string(subscription_row['State'])
        country = clean_string(subscription_row['Country'])
        post_code = clean_string(subscription_row['Postcode'])

        if address_line_1:
            subscriber_address.address_1 = address_line_1

        # attempt to best fit address_line_2 and address_line_3 into subscriber_address.address_2
        if address_line_2 and address_line_3:
            subscriber_address.address_2 = " ".join([address_line_2, address_line_3])
        elif address_line_2:
            subscriber_address.address_2 = address_line_2
        elif address_line_3:
            subscriber_address.address_2 = address_line_3
        # else both address_line_2 and address_line_3  are blank

        # doesn't read nicely, but the equivalence is (city < region) == (suburb < state)
        if suburb:
            subscriber_address.city = suburb
        if state:
            subscriber_address.region = state

        # expect country and postcode to be non empty
        subscriber_address.country = country
        subscriber_address.postal_code = post_code

        post_process_address(subscriber_address)

        subscriber_address.address_usable = True if subscription_row['Address_usable'] == 'Y' else False
        subscriber_address.home_phone = clean_string(subscription_row['Home_phone'])
        subscriber_address.work_phone = clean_string(subscription_row['Work_phone'])
        subscriber_address.mobile = clean_string(subscription_row['Mobile'])
        subscriber_address.save()

    return subscriber_address

def create_gift_giver_address(subscription_row, product_code, gift_giver):
        imported_id='%s:%s:gg' % (product_code, subscription_row['Payer_ID'])
        try:
            gift_giver_address = Address.objects.get(imported_id=imported_id, user=gift_giver)
        except Address.DoesNotExist:
            gift_giver_address = Address(imported_id=imported_id, user=gift_giver)

            address_data = {}
            address = []

            # uses Payer_label_line_2, Payer_label_line_3, Payer_label_line_4, Payer_label_line_5, Payer_label_line_6, Payer_label_line_7, Payer_label_line_8
            for i in xrange(2, 9):
                address.append(subscription_row['Payer_label_line_%d' % i])

            for i in xrange(len(address)-1, 0, -1):
                if address[i] == '':
                    continue

                first_non_blank = i
                break

            first_non_blank_val = address[first_non_blank]

            postcode = re.search(r'(\d+)$', first_non_blank_val)

            if postcode:
                address_data['postal_code'] = postcode.group(1)
                address_data['region']  = first_non_blank_val[:-len(address_data['postal_code'])]
            else:
                address_data['country'] = first_non_blank_val
                region = address[first_non_blank]

            for i in xrange(0, first_non_blank):
                if address_data.get('country') == 'United Kingdom':
                    postcode = re.search(r'(\w{3} \w{3})$', address[i])
                else:
                    postcode = re.search(r'[^(unit|box)]\s+(\d{3,})$', address[i], re.I)

                if postcode:
                    address_data['postal_code'] = postcode.group(1)

                    address_data[address_keys[i]] = address[i][:-len(address_data['postal_code'])]
                else:
                    address_data[address_keys[i]] = address[i]

                if address_data[address_keys[i]].find('  ') != -1:
                    split_city = address_data[address_keys[i]].split('  ')

                    address_data['region'] = split_city[-1].strip()
                    address_data[address_keys[i]] = split_city[0].strip()

            if not address_data.has_key('country') or address_data['country'] == 'New Zealan':
                address_data['country'] = 'New Zealand'

            # save data to address
            for key in address_keys:
                if address_data.has_key(key):
                    # replace excess spaces
                    while address_data[key].find('  ') != -1:
                        address_data[key] = address_data[key].replace('  ', ' ')

                    setattr(gift_giver_address, key, clean_string(address_data[key]))

            post_process_address(gift_giver_address)
            gift_giver_address.save()

        return gift_giver_address

def post_process_address(address):
    if address:
        if address.country == 'New Zealand':
            # this seems semantically wrong, but the logic is to put the largest areas in the region column.
            # move an NZ city/town into the 'region' column if it is unset and currently in the 'city' column
            if address.city and not address.region and address.city.lower() in nz_cities_and_towns:
                address.region = address.city
                address.city = None

            # fix 3 digit NZ post codes
            if address.postal_code and len(address.postal_code) == 3:
                address.postal_code = ''.join(['0', address.postal_code])

        # move Street or Rural Delivery addresses out of city
        if address.city and not address.address_2:
            if any(i in address.city.lower() for i in non_cities) or re.search(r'^RD\s?\d+$', address.city, re.I):
                address.address_2 = address.city
                address.city = None

        # move suburbs (idenftifed by non-cities list and non-numeric) out of address_2
        if address.address_2 and not address.city and \
                re.search(r'^[^0-9]+$', address.address_2, re.I) and all(i not in address.address_2.lower() for i in non_cities):
            address.city = address.address_2
            address.address_2

        # convert any None fields to empty strings to conform to convention (and prevent save errors!)
        char_fields = address_keys + ['home_phone', 'work_phone', 'mobile']
        for field_name in char_fields:
            if hasattr(address, field_name):
                field_value = getattr(address, field_name)
                if field_value == None:
                    setattr(address, field_name, '')

    return address

def create_sub_offer(subscription_row, product, sub_code, issues_per_year, subcodes_dict):
    sub_offer_imported_id = '%s:%s' % (product.slug, sub_code)

    try:
        sub_offer = SubscriptionOffer.objects.get(imported_id=sub_offer_imported_id)
    except SubscriptionOffer.DoesNotExist:
        sub_code_description = clean_string(subscription_row['Sub_code_description'])
        sub_offer = SubscriptionOffer(code=sub_code, imported_id=sub_offer_imported_id, **{'medium': 'magazine',
                'area': 'nz',
                'code_description': sub_code_description,
                'product': product
            })

        # calculate the the issue count and term of this sub offer
        current_sub_code_dict = subcodes_dict[sub_code]
        if not current_sub_code_dict:
            exit("Unknown subcode (%s, %s), exiting..." % (sub_code, sub_code_description))

        issue_count_raw = current_sub_code_dict['Issues']
        if issue_count_raw and issue_count_raw.isalpha() and issue_count_raw.strip().lower() == 'life':
            sub_offer.life = True
        elif issue_count_raw:
            sub_offer.num_issues = int(float(issue_count_raw))
            sub_offer.term = (12 / issues_per_year) * sub_offer.num_issues
        else:
            exit("Can't calculate issue count for %s: %s - %s, exiting..." % (product.slug, sub_code, sub_code_description))

        # any sub offer with a description in this column indicates it is legacy
        is_sub_offer_usable = current_sub_code_dict.get('Description (usable)')
        if is_sub_offer_usable and is_sub_offer_usable.strip():
            sub_offer.active = True
            # TODO: sub_offer.public will be set manually

        sub_offer_price = current_sub_code_dict.get('Full amt')
        if sub_offer_price and sub_offer_price.strip():
            sub_offer.subscription_price = float(sub_offer_price.lstrip('$'))

        sub_offer_cover_price = current_sub_code_dict.get('Copy val')
        if sub_offer_cover_price and sub_offer_cover_price.strip():
            sub_offer.cover_price = float(sub_offer_cover_price.lstrip('$'))

        # 'S' indicates standard (paid), 'F' indicates free
        is_sub_offer_free = current_sub_code_dict.get('Type')
        if is_sub_offer_free and is_sub_offer_free.strip() == 'F':
            sub_offer.type = 2

        grace_copies = current_sub_code_dict.get('Grace')
        if grace_copies and grace_copies.strip():
            sub_offer.grace_copies = int(grace_copies.strip())

        sub_offer.save()

    return sub_offer

def create_subscription(subscription_row, product, sub_offer, subscriber, subscriber_address, gift_giver, current_issue_num):
    issues_remaining =  None
    is_life_subscription = False

    issues_remaining_raw = clean_string(subscription_row['Issues_remaining'])
    expiry_issue_raw = clean_string(subscription_row['Expiry_issue'])
    sub_start_date = string_to_datetime(clean_string(subscription_row['Date_of_first_subscription']))

    subscription = Subscription(imported_id='%s:%s:%s:%s' % (product.slug, subscription_row['Id'], sub_offer.code, 'subsplus'), **{'subscription_offer': sub_offer,
            'price': sub_offer.subscription_price,
            'effort': effort,
            'subscriber': subscriber,
            'gift_giver': gift_giver,
            'address': subscriber_address,
            'copies_per_issue': int(subscription_row['Copies_per_issue'])
        })

    # check for a life subscription
    is_sub_offer_life = sub_offer.life
    is_issues_remaining_life = True if (issues_remaining_raw and issues_remaining_raw.lower() == 'life') else False
    if is_sub_offer_life:
        is_life_subscription = True
    elif is_issues_remaining_life:
        is_life_subscription = True
        add_subscription_import_msg(subscription, 'life subscription but subcode is finite')
    else:
        try:
            issues_remaining = int(issues_remaining_raw)
        except:
            exit("Can't parse issues remaining ('%s') in row id %s, exiting..." % (issues_remaining_raw, subscription_row['Id']))

    if not is_life_subscription:
        # find and add expiry issue
        if expiry_issue_raw and expiry_issue_raw in issue_cache:
            expiry_issue_num = issue_cache[expiry_issue_raw].number
            add_issue_alias(product, expiry_issue_num, expiry_issue_raw)
        else:
            expiry_issue_num = current_issue_num + issues_remaining
            add_subscription_import_msg(subscription, 'expiry issue not found')

        subscription.expiry_issue = issue_cache[expiry_issue_num]

        # find and add start issue
        sub_offer_num_issues = sub_offer.num_issues
        if sub_offer_num_issues >= 0:
            first_issue_num = expiry_issue_num - sub_offer_num_issues + 1
        else:
            first_issue = Issue.objects.filter(pub_date__gte=sub_start_date, product=product).order_by('pub_date')[0]
            first_issue_num = first_issue.number
            add_subscription_import_msg(subscription, 'calculated first issue')

        #hopefully this is not possible, but cater for it anyway (GG have done some weird stuff with sub offer fixups)
        if first_issue_num > expiry_issue_num:
            first_issue_num = expiry_issue_num
            add_subscription_import_msg(subscription, 'calculated zero or negative length term')

        subscription.first_issue = issue_cache[first_issue_num]

        subscription.save()
    else:
        first_issue = Issue.objects.filter(pub_date__gte=sub_start_date, product=product).order_by('pub_date')[0]
        first_issue_num = first_issue.number
        subscription.first_issue = issue_cache[first_issue_num]
        subscription.save()

    for sent_sub_num in xrange(first_issue_num, current_issue_num + 1):
        sent_issue = issue_cache[sent_sub_num]
        sent_sub = SentSubscription(subscription=subscription, issue=sent_issue, date_sent=sent_issue.pub_date)
        sent_sub.save()

def cache_issues(product):
     #build a issue cache for fast lookups, key on issue number AND its subsplus alias
     issues = Issue.objects.filter(product=product)
     for issue in issues:
        issue_cache[issue.number] = issue
        if issue.subs_plus_alias:
            issue_cache[issue.subs_plus_alias] = issue

def add_issue_alias(product, issue_num, alias):
    # update the issues alias, non critical but helpful to identify problems with issue provisioning
    if alias:
        issue = issue_cache[issue_num]
        #add the alias if required
        if not issue.imported_aliases:
            issue.imported_aliases = alias
            issue.save()
        elif alias not in issue.imported_aliases:
            issue.imported_aliases = ",".join([issue.imported_aliases, alias])
            issue.save()

def add_subscription_import_msg(subscription, message):
    if subscription.post_import_validation_msg:
        subscription.post_import_validation_msg = ",".join([subscription.post_import_validation_msg, message])
    else:
        subscription.post_import_validation_msg = message
    flagged_subscriptions[subscription.imported_id] = "imported_id=%s, name=%s, message=%s" % (subscription.imported_id,
        subscription.subscriber.full_name, subscription.post_import_validation_msg)
    #deliberately does not save(), will be done in create_subscription()

def process_subscription_row(row, product, issues_per_year, current_issue_number, subcodes_dict):
    # create user for subscriber
    email = clean_string(row['Email_address'])
    subscriber, subscriber_created = TangyUser.objects.get_or_create(imported_id='%s:%s:sub' % (product.slug, row['Id']), defaults = {
        'first_name': clean_string(row['Given_name']),
        'last_name': clean_string(row['Surname']),
        'salutation': clean_string(row['Salutation']),
        'org_title': clean_string(row['Job']),
        'org_name': clean_string(row['Company_name']),
        'email': email
    })

    subscriber_address = create_subscriber_address(row, subscriber, product.slug)

    # create the gift giver
    gift_giver = None
    if row['Payer_label_line_1'] != '':
        gift_giver, gift_giver_created = TangyUser.objects.get_or_create(imported_id='%s:%s:gg' % (product.slug, row['Id']), defaults = {
            'first_name': clean_string(row['Payer_label_line_1']),
            'salutation': clean_string(row['Payer_salutation']),
        })

        create_gift_giver_address(row, product.slug, gift_giver)

    #retrieve or create the subscription offer
    sub_code = clean_string(row['Subscription_code'])

    if sub_offer_cache.has_key(sub_code):
        sub_offer = sub_offer_cache[sub_code]
    else:
        sub_offer = create_sub_offer(row, product, sub_code, issues_per_year, subcodes_dict)
        sub_offer_cache[sub_code] = sub_offer

    create_subscription(row, product, sub_offer, subscriber, subscriber_address, gift_giver, current_issue_number)

def do_import(skip_legacy, current_issue_number, subscriptions_reader_dict, subcodes_dict, magazine_meta_dict):
    errors = []

    product = None
    issues_per_year = None
    num_rows_procesed = 0

    for row in subscriptions_reader_dict:
        try:
            print "%d. Processing %s, %s %s, %s" % (num_rows_procesed, row['Id'], row['Given_name'], row['Surname'],
                row['Subscription_code'])
            num_rows_procesed+=1

            # all products should already be provisioned, find it.
            if product == None:
                subsplus_product_name = row['Publication'].strip()
                product = Product.objects.get(slug=magazine_meta_dict[subsplus_product_name]['slug'])
                issues_per_year = int(magazine_meta_dict[subsplus_product_name]['issues_per_year'])
                cache_issues(product)

            if skip_legacy and int(row['Issues_remaining']) < 0:
                continue

            process_subscription_row(row, product, issues_per_year, current_issue_number, subcodes_dict)

        except ValueError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            errors.append([traceback.format_exc().splitlines(), row])
            continue

    for tb, row in errors:
        for tb_line in tb:
            print tb_line

        print row

    if flagged_subscriptions:
        print "\nFlagged subscriptions: "
        for v in flagged_subscriptions:
            print "%s" % flagged_subscriptions[v]

def main():
    start_time_secs = time.time()
    from sys import argv

    skip_legacy = False

    try:
        subscriptions_csv = argv[1]
        magazine_subcodes = argv[2]
        magazine_meta = argv[3]
        current_issue_number = int(argv[4])
    except:
        print "Error loading csv files, provide 1) the subscriber data 2) magazine_subcodes 3) magazine meta 4) current issue number (this must be accurate relative to the subscriber csv)"
        sys.exit()

    try:
        skip_legacy = (argv[5] == 'skip')
    except:
        pass

    do_import(skip_legacy, current_issue_number, *load_csv_files(subscriptions_csv, magazine_subcodes, magazine_meta))

    finish_time_secs = time.time()
    print "\nDone in %s" % datetime.timedelta(seconds=finish_time_secs-start_time_secs)

def load_csv_files(subscriptions_csv, magazine_subcodes, magazine_meta):
    # see subsplus_resources for schemas

    # index all the sub codes by code
    reader = csv.DictReader(open(magazine_subcodes))
    subcodes_dict = {}
    for row_dict in reader:
        subcodes_dict[row_dict['Code']] = row_dict
    if not subcodes_dict:
        exit("Provide valid magazine_subcodes, %s is unusable" % magazine_subcodes)

    # index magazine meta by subsplus publication name AND slug
    reader = csv.DictReader(open(magazine_meta))
    magazine_meta_dict = {}
    for row_dict in reader:
        magazine_meta_dict[row_dict['subsplus_publication']] = row_dict
        magazine_meta_dict[row_dict['slug']] = row_dict
    if not magazine_meta_dict:
        exit("Provide valid magazine_meta, %s is unusable" % magazine_meta)

    subscriptions_reader_dict = csv.DictReader(open(subscriptions_csv))

    return (subscriptions_reader_dict, subcodes_dict, magazine_meta_dict)

if __name__ == '__main__':
    main()
