# ga-cl

Simple Google Analytics command line tools for Python (2.7+).

## Get started

Follow steps 1 and 2 here: https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/installed-py to create the Google Cloud project and download the client_secrets.json file.

Clone this project to a directory in your hard drive with `git clone https://github.com/sahava/ga-cl.git`.

Create a new directory in the root of this project named `secret/ `, and copy the client_secrets.json file to this directory.

Now you should have two directories in your project root: `secret/` and `modules/`.

## Authenticate against the tools

When you run any of the python modules, a web browser will open, and you will be prompted to login with the Google account you want to run the module API calls against. Once you have authenticated, this authentication is stored in the `analytics.dat` file in the `secret/` directory.

To remove authentication, simply delete this file.

The modules might require different levels of authentication, so when moving from one module to the next, remove the `analytics.dat` file to re-authenticate.

# ga_permissions_to_csv.py

**Requires:**

Allow the tool to read your Google Analytics account data.

**Run:**

`python ga_permissions_to_csv.py [-a account_id,account_id2,account_id3] path_to_client_secrets`

This module creates a CSV file of the GA accounts you have access to, with the user permissions listed for each account in their respective CSV file. You need Manage Users access to each GA account for which a file is created.

You can provide a list of Google Analytics Account IDs to the `-a` argument, or you can drop the `-a` argument to create CSV files for all the accounts you have sufficient access to.

`path_to_client_secrets` is a relative path to where the client_secrets.json file is stored.

Once the command is run, a new directory `csv/` is created, where all the CSV files (one for each account) are stored. These files contain the user permission information for each respective account.

**Example:**

`python ga_permissions_to_csv.py ../secret/client_secrets.json`

# data_retention.py

**Requires:**

Allow the tool to read and edit your account, property, and view settings.

To update the settings, you need EDIT access to each property you want to update.

**Run:**

`python data_retention.py (-c | -u PATH) path_to_client_secrets`

This module can be used to create (`-c`) a CSV file in the `csv/` directory named `data_retention_list.csv`. This file contains a row for every web property the logged in user has access to. Each row shows the current data retention settings (TTL and Reset) for each respective property.

You can also use this to mass update (`-u PATH_TO_CSV`) the properties, using the CSV file created by `-c` as the source data (`PATH_TO_CSV` should be the path to this CSV file). The tool checks if the data retention TTL and/or Reset values have been changed, and if they have, you are prompted whether you want to update the properties with the new values or not.

Valid values for TTL are MONTHS_14, MONTHS_26, MONTHS_38, MONTHS_50, INDEFINITE.

Valid values for Reset are True, False.

**Examples:**

`python data_retention.py -c ../secret/client_secrets.json`

`python data_retention.py -u csv/data_retention_list.csv ../secret/client_secrets.json`
