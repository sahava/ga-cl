import sys
import auth
import json
import argparse
import re

def link_filters(service, created_filters, account_id):
    ua_regex = re.compile(r'^UA-\d+-\d+$', re.IGNORECASE)
    property_input = ''
    while ua_regex.match(property_input) is None and property_input is not 'q':
        property_input = raw_input('Please enter the Web Property ID (e.g. UA-%s-1) of the web property in which the links will be created (enter \'q\' to quit): ' % account_id)
    if property_input is 'q':
        sys.exit()
    
    pid_regex = re.compile(r'^\d+$')
    profile_input = ''
    while pid_regex.match(profile_input) is None and profile_input is not 'q':
        profile_input = raw_input('Please enter the Profile ID of the Google Analytics profile that you want to link the filters to (enter \'q\' to quit): ')
    if profile_input is 'q':
        sys.exit()
      
    first_rank = None;
    last_rank = 1;
    for filter in created_filters:
        print('Linking filter %s to profile %s in web property %s' % (filter.get('name'), profile_input, property_input))
        created_link = service.management().profileFilterLinks().insert(
            accountId=account_id,
            webPropertyId=property_input,
            profileId=profile_input,
            body={
                'filterRef': {
                    'id': filter.get('id')
                }
            }
        ).execute()
        if first_rank is None:
            first_rank = created_link.get('rank')
        last_rank = created_link.get('rank')
    if len(created_filters) is 1:
        print('Successfully created 1 filter in profile %s in position %s\n' % (profile_input, first_rank))
    else:
        print('Successfully created %s filters in profile %s in positions %s to %s\n' % (len(created_filters), profile_input, first_rank, last_rank))
    
    yes_no = False
    while yes_no not in ['y', 'n']:
        yes_no = raw_input('Add another profile link (y/n)? ')
    if yes_no is 'n':
        sys.exit()
    link_filters(service, created_filters, account_id)        
          

def create_filters(service, json_path, account_id):
    created_filters = []
    with open(json_path) as myfile:
        myfile = json.load(myfile)
        for filter in myfile:
            print('Creating filter %s in account %s' % (filter.get('name'), account_id))
            created_filters.append(
                service.management().filters().insert(
                    accountId=account_id,
                    body=filter
                ).execute()
            )
    print('Successfully created %s filters in account %s\n' % (len(created_filters), account_id))
    return created_filters
            

def main(argv):
    scope = ['https://www.googleapis.com/auth/analytics.edit']

    parser = argparse.ArgumentParser(description='Create and link filters to a Google Analytics account/profile. You will need the Google Analytics Account ID, Web Property ID (UA-XXXXX-Y), and the Profile ID at hand. You can find the Account ID and Profile ID in the URL of the Google Analytics UI (when viewing any profile). Account ID is the numerical string after \'a\' and Profile ID is the numerical string after \'p\' in the URL\'s /aXXXXwXXXXpXXXX part.')
    
    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--create', metavar='accountid', help='Create the filters in the given Google Analytics account ID', required=True, dest='accountid')
    required.add_argument('-j', '--jsonpath', help='The path to the JSON file', required=True, metavar='/path/to/file.json')
    
    parser.add_argument('path_to_client_secrets', help='Path to your client_secrets file')
    
    args = parser.parse_args()

    account_id = args.accountid
    json_path = args.jsonpath
    client_secrets_path = args.path_to_client_secrets

    service = auth.auth('analytics', 'v3', scope, client_secrets_path)
    
    created_filters = create_filters(service, json_path, account_id)
    
    yes_no = False
    while yes_no not in ['y', 'n']:
        yes_no = raw_input('Do you wish to link these filters to a Google Analytics profile (y/n)? ')
    if yes_no is 'n':
        sys.exit()
    
    link_filters(service, created_filters, account_id)


if __name__ == '__main__':
    main(sys.argv[1:])
