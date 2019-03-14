import sys
import auth
import argparse
import os
import csv
import re

from googleapiclient.errors import HttpError


def get_accounts(service, accounts):
    print('Fetching account details...')
    account_list_from_api = service.management().accountSummaries().list(fields='items(id,name)').execute()

    if accounts == 'all':
        return account_list_from_api.get('items', [])

    accounts_as_list = accounts.split(',')

    def check_if_account_in_args(account):
        return account['id'] in accounts_as_list

    return list(filter(check_if_account_in_args, account_list_from_api.get('items', [])))


def get_permissions(service, aid):
    try:
        permissions = service.management().accountUserLinks().list(accountId=aid, fields='items(permissions/effective,userRef/email)').execute()
        return permissions.get('items')
    except HttpError as e:
        if 'insufficientPermission' in e.content:
            print('Skipping due to insufficient rights to view account permissions.')
        else:
            print(e.content)
        return None


def get_valid_filename(s):
    """
    Adapted from https://github.com/django/django/blob/master/django/utils/text.py
    """
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s).lower()


def build_csv(permissions, account):
    with open('csv/%s_%s.csv' % (get_valid_filename(account['name']), account['id']), 'wb') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['Account name', 'Account ID', 'Email address', 'Permission'])
        for permission in permissions:
            effective = '|'.join(permission.get('permissions', {}).get('effective', []))
            wr.writerow([account['name'].encode('utf-8'), account['id'], permission['userRef']['email'], effective])


def main(argv):
    scope = ['https://www.googleapis.com/auth/analytics.readonly',
             'https://www.googleapis.com/auth/analytics.manage.users']

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--accounts', default='all', metavar='accounts', help='comma-separated list of account IDs to pull permissions for')
    parser.add_argument('path_to_client_secrets', help='path to your client_secrets file')
    args = parser.parse_args()

    accounts = args.accounts
    client_secrets_path = args.path_to_client_secrets

    service = auth.auth('analytics', 'v3', scope, client_secrets_path)

    account_list = get_accounts(service, accounts)

    if len(account_list) == 0:
        if accounts == 'all':
            print('Your Google ID doesn\'t have access to any Google Analytics accounts!')
        else:
            print('You don\'t have permissions to access any of the accountIds you listed in the arguments!')

    for account in account_list:
        print('\nFetching permissions for account "%s" (%s)...' % (account['name'], account['id']))
        permissions = get_permissions(service, account['id'])
        if permissions:
            print('Building "csv/%s_%s.csv"...' % (get_valid_filename(account['name']), account['id']))
            if not os.path.exists('csv'):
                os.makedirs('csv')
            build_csv(permissions, account)


if __name__ == '__main__':
    main(sys.argv[1:])
