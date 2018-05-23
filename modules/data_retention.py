import sys
import auth
import argparse
import os
import csv
import re
import json

from googleapiclient.errors import HttpError

HEADERS=['Account name', 'Account ID', 'Web Property Name', 'Web Property ID', 'Data Retention TTL', 'Data Retention Reset On New Activity']
VALID_TIME=['MONTHS_14', 'MONTHS_26', 'MONTHS_38', 'MONTHS_50','INDEFINITE']
VALID_RESET=['True', 'False']

def valid_headers(headers):
    valid = True
    for idx, val in enumerate(headers):
        if val != HEADERS[idx]:
            valid = False
    return valid


def build_hierarchy(service):
    hierarchy = {}
    accounts_list = get_accounts(service)
    print('Building account and property hierarchy. Please wait, this might take a minute...')
    for account in accounts_list:
        aid = account['id']
        properties_list = get_properties(service, account['id'])
        hierarchy[aid] = {
            'account_id': aid,
            'account_name': account['name'],
            'properties': {}
        }
        for property in properties_list:
            pid = property['id']
            hierarchy[aid]['properties'][pid] = {
                'property_id': pid,
                'property_name': property['name'],
                'data_retention_ttl': str(property['dataRetentionTtl']),
                'data_retention_reset': str(property['dataRetentionResetOnNewActivity']),
                'website_url': property.get('websiteUrl')
            }
    return hierarchy


def get_accounts(service):
    print('Fetching account list...')
    account_list_from_api = service.management().accountSummaries().list(
        fields='items(id,name)'
    ).execute()

    return account_list_from_api.get('items', [])


def get_properties(service, account_id):
    property_list_from_api = service.management().webproperties().list(
      accountId=account_id,
      fields='items(id,name,websiteUrl,dataRetentionTtl,dataRetentionResetOnNewActivity)'
    ).execute()
    
    return property_list_from_api.get('items', [])


def update_retention(service, account_id, property_id, property_name, website_url, new_ttl, new_reset):
    service.management().webproperties().update(
        accountId=account_id,
        webPropertyId=property_id,
        body={
            'name': property_name,
            'websiteUrl': website_url,
            'dataRetentionTtl': new_ttl,
            'dataRetentionResetOnNewActivity': new_reset
        }
    ).execute()


def parse_csv_and_update(path, service):
    skip_accounts = []
    always_yes = False
    with open(path, 'r') as myfile:
        retention_list=csv.reader(myfile)
        headers=retention_list.next()
        print('Validating CSV headers...')
        if len(headers) is not 6 or not valid_headers(headers):
            print('Invalid CSV file')
        else:
            hierarchy=build_hierarchy(service)
            print('\nROW: MESSAGE')
            for idx,row in enumerate(retention_list):
                row_no = idx + 2
                current_account_id = row[1]
                current_property_name = row[2]
                current_property_id = row[3]
                current_retention_ttl = row[4]
                current_retention_reset = row[5]
                if current_account_id in skip_accounts:
                    continue
                found_account = hierarchy.get(current_account_id)
                if found_account is None:
                    print('%s: No access to account with ID %s, skipping...' % (row_no, current_account_id))
                    skip_accounts.append(current_account_id)
                    continue
                found_property = found_account['properties'].get(current_property_id)
                if found_property is None:
                    print('%s: No access to property with ID %s, skipping...' % (row_no, current_property_id))
                    continue
                if current_retention_ttl == found_property['data_retention_ttl'] and current_retention_reset == found_property['data_retention_reset']:
                    print('%s: No changes to retention settings for %s, skipping...' % (row_no, current_property_id))
                    continue
                if current_retention_ttl not in VALID_TIME:
                    print('%s: Retention time for %s not one of MONTHS_14, MONTHS_26, MONTHS_38, MONTHS_50, or INDEFINITE, skipping...' % (row_no, current_property_id))
                    continue
                if current_retention_reset not in VALID_RESET:
                    print('%s: Retention reset for %s not one of True or False, skipping...' % (row_no, current_property_id))
                    continue
                if always_yes:
                    print('%s: UPDATING property "%s" (%s) with Data Retention TTL of "%s" and Data Retention Reset On New Activity of "%s"...' % (row_no, found_property['property_name'], current_property_id, current_retention_ttl, current_retention_reset))
                    try:
                        update_retention(service, current_account_id, current_property_id, found_property['property_name'], found_property['website_url'], current_retention_ttl, current_retention_reset)
                        print('\tDONE')
                    except HttpError as err:
                        print('\tERROR: %s, skipping...' % json.loads(err.content)['error']['message'])
                    continue
                print('%s: UPDATE property "%s" (%s)' % (row_no, found_property['property_name'], current_property_id))
                print('\tPrevious Data Retention TTL: %s\tNew Data Retention TTL: %s' % (found_property['data_retention_ttl'], current_retention_ttl))
                print('\tPrevious Data Retention Reset: %s\tNew Data Retention Reset: %s' % (found_property['data_retention_reset'], current_retention_reset))
                response = raw_input('\ty for yes, n for no, a for always yes, q for quit: ')
                while response not in ['y', 'n', 'a', 'q']:
                    response = raw_input('\tPlease type one of the letters y/n/a/q and press ENTER: ')
                if response == 'n':
                    continue
                if response == 'q':
                    break
                if response == 'a':
                    always_yes = True
                    print('\tUPDATING property "%s" (%s) with Data Retention TTL of "%s" and Data Retention Reset On New Activity of "%s"...' % (found_property['property_name'], current_property_id, current_retention_ttl, current_retention_reset))
                    try:
                        update_retention(service, current_account_id, current_property_id, found_property['property_name'], found_property['website_url'], current_retention_ttl, current_retention_reset)
                        print('\tDONE')
                    except HttpError as err:
                        print('\tERROR: %s, skipping...' % json.loads(err.content)['error']['message'])
                    continue
                if response == 'y':
                    print('\tUPDATING property "%s" (%s) with Data Retention TTL of "%s" and Data Retention Reset On New Activity of "%s"...' % (found_property['property_name'], current_property_id, current_retention_ttl, current_retention_reset))
                    try:
                        update_retention(service, current_account_id, current_property_id, found_property['property_name'], found_property['website_url'], current_retention_ttl, current_retention_reset)
                        print('\tDONE')
                    except HttpError as err:
                        print('\tERROR: %s Skipping...' % json.loads(err.content)['error']['message'])
                    continue

                    
def main(argv):
    scope = ['https://www.googleapis.com/auth/analytics.edit']

    parser = argparse.ArgumentParser(
       description='List and mass update Google Analytics data retention settings per web property.'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--create', help='create CSV-file of all web properties and their data retention settings', action='store_true')
    group.add_argument('-u', '--update', metavar='PATH', help='path to the CSV-file that is the source for the mass update')
    parser.add_argument('path_to_client_secrets', help='path to your client_secrets file')
    args = parser.parse_args()

    client_secrets_path = args.path_to_client_secrets

    service = auth.auth('analytics', 'v3', scope, client_secrets_path)

    if args.create:
        if not os.path.exists('csv'):
            os.makedirs('csv')
        with open('csv/data_retention_list.csv', 'w') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(HEADERS)
            hierarchy=build_hierarchy(service)
            print('Writing data to CSV...')
            for account in hierarchy:
                for property in hierarchy[account]['properties']:
                    wr.writerow([
                        hierarchy[account]['account_name'].encode('utf-8'),
                        hierarchy[account]['account_id'],
                        hierarchy[account]['properties'][property]['property_name'].encode('utf-8'),
                        hierarchy[account]['properties'][property]['property_id'],
                        hierarchy[account]['properties'][property]['data_retention_ttl'],
                        hierarchy[account]['properties'][property]['data_retention_reset']
                    ])
            print('All done! File data_retention_list.csv has been written in the csv/ folder.')
    
    if args.update:
        path = args.update
        print('Validating CSV file structure...')
        if not path.lower().endswith('.csv'):
            print('The file must have the .csv filetype!')
        else:
            parse_csv_and_update(path, service)
                
                
if __name__ == '__main__':
    main(sys.argv[1:])
