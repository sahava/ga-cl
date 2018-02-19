import argparse

import httplib2

from apiclient.discovery import build
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def auth(api_name, api_version, scope, client_secrets_path):

    secret_folder = client_secrets_path.rsplit('/', 1)[0] + '/'
  
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])
  
    # Set up a Flow object tobe used if we need to authenticate
    flow = client.flow_from_clientsecrets(
        client_secrets_path,
        scope=scope,
        message=tools.message_if_missing(client_secrets_path))
    
    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid, run through the native client
    # flow. The Storage object will ensure that if successful, the good
    # credentials will be written back to a file.
    storage = file.Storage(secret_folder + api_name + '.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())
    
    # Build the service object
    service = build(api_name, api_version, http=http)
    
    return service