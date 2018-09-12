import sys
import auth
import json
import argparse

def link_filters(service, created_filters, account_id, web_property_id, profile_id):
    first_rank = None;
    last_rank = 1;
    for filter in created_filters:
        print("Linking filter %s to profile %s in web property %s" % (filter.get('name'), profile_id, web_property_id))
        created_link = service.management().profileFilterLinks().insert(
            accountId=account_id,
            webPropertyId=web_property_id,
            profileId=profile_id,
            body={
                'filterRef': {
                    'id': filter.get('id')
                }
            }
        ).execute()
        if first_rank is None:
            first_rank = created_link.get('rank')
        last_rank = created_link.get('rank')
    print('Successfully created %s filters in profile %s in positions %s to %s' % (len(created_filters), profile_id, first_rank, last_rank))
          

def create_filters(service, json_path, account_id):
    created_filters = []
    with open(json_path) as myfile:
        myfile = json.load(myfile)
        for filter in myfile:
            print("Creating filter %s in account %s" % (filter.get('name'), account_id))
            created_filters.append(
                service.management().filters().insert(
                    accountId=account_id,
                    body=filter
                ).execute()
            )
    print("Successfully created %s filters in account %s" % (len(created_filters), account_id))
    return created_filters
            

def main(argv):
    scope = ['https://www.googleapis.com/auth/analytics.edit']

    parser = argparse.ArgumentParser(description='Create and link filters to a Google Analytics account/profile. You can get the Account ID and the Profile ID from the URL when viewing a profile in the Google Analytics UI. The Account ID is the string after "a" and the Profile ID is the string after "p" in the URL\'s /a12345w12345p12345 part.')
    
    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--create', metavar='accountid', help='Create the filters in the given Google Analytics account ID', required=True, dest='accountid')
    required.add_argument('-j', '--jsonpath', help='The path to the JSON file', required=True, metavar='/path/to/file.json')
    
    parser.add_argument('path_to_client_secrets', help='Path to your client_secrets file')
    parser.add_argument('-w', '--webpropertyid', metavar='UA-XXXXX-Y', help='Web property ID where the filters will be linked to a profile')
    parser.add_argument('-p', '--profileid', metavar='profileid', help='Google Analytics profile ID to which you want to link the filters')
    
    args = parser.parse_args()

    account_id = args.accountid
    json_path = args.jsonpath
    web_property_id = args.webpropertyid
    profile_id = args.profileid
    client_secrets_path = args.path_to_client_secrets

    service = auth.auth('analytics', 'v3', scope, client_secrets_path)
    
    created_filters = create_filters(service, json_path, account_id)
    if web_property_id is not None and profile_id is not None:
        link_filters(service, created_filters, account_id, web_property_id, profile_id)


if __name__ == '__main__':
    main(sys.argv[1:])
