# -*- coding: utf8 -*-

import dateutil.parser
import datetime
import json
import requests
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())

class Dropbox(object):
    """Wrapper to Dropbox's HTTP API:
        https://www.dropbox.com/developers/documentation/http/documentation#files-list_folder"""

    dropbox_error_codes = {
        'bad_input': 400,
        'bad_token': 401,
        'unknown': 409,
        'too_many_requests': 429
    }

    dropbox_endpoints = {
        'list_folder': 'https://api.dropboxapi.com/2/files/list_folder',
        'list_folder_continue': 'https://api.dropboxapi.com/2/files/list_folder/continue',
        'download': 'https://content.dropboxapi.com/2/files/download'
    }

    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + self.token,
                                     'Content-Type': 'application/json'})

    def get_own_budgets(self):
        return self.get_all_budgets_at_path('/YNAB')

    def get_their_budgets(self):
        """Assumes shared budgets are available through a shared folder at the
        root named 'YNAB (1)'. The '(1)' is because the own user's 'YNAB'
        folder already exists, so when accepting a folder share from another
        person, Dropbox will append '(1)' to avoid a name clash. This limits
        comparisons to one other person's budget(s), as when a second person
        shares their budget(s), it will appear as 'YNAB (2)'."""
        return self.get_all_budgets_at_path('/YNAB (1)')

    def get_all_budgets_at_path(self, path):
        url = self.dropbox_endpoints['list_folder']
        data = {
            'path': path,
            'recursive': False,
            'include_media_info': False,
            'include_deleted': False
        }

        r = self.session.post(url, data=json.dumps(data))

        if r.status_code == requests.codes.ok:
            try:
                ynab_contents = r.json()
            except ValueError:
                self.raise_exception(r, 'Could not retrieve list of budgets')
        else:
            self.raise_exception(r, 'Could not retrieve list of budgets')

        budgets = []

        for entry in ynab_contents['entries']:
            if entry['.tag'] == 'folder' and 'ynab4' in entry['name']:
                # YNAB stores budgets as folders, delimiting their name with
                # '~', a numeric ID, and the '.ynab4' faux extension.
                budget_pretty_name = entry['name'].split('~')[0]
                budget_id = entry['id']
                budget_path = entry['path_lower']

                budgets.append({
                    'name': budget_pretty_name,
                    'id': budget_id,
                    'path': budget_path
                })

        return budgets

    def raise_exception(self, request, message=""):
        raise Exception('{message}\nStatus: {error_code}\nMessage: {error_message}'
                    .format(message=message,
                            error_code=request.status_code,
                            error_message=request.text))

    def get_budget_file(self, budget_directory_path):
        data = {
            'path': budget_directory_path,
            'recursive': True,
            'include_media_info': False,
            'include_deleted': False
        }

        budget_dir_contents_response = self.session.post(
            self.dropbox_endpoints['list_folder'],
            data=json.dumps(data)
        )

        if budget_dir_contents_response.status_code == requests.codes.ok:
            try:
                # TODO deal with has_more. Up to ~2000 files we're OK.
                # http://stackoverflow.com/questions/34237283/dropbox-api-list-folder-functions
                budget_dir_contents = budget_dir_contents_response.json()
            except ValueError:
                self.raise_exception(budget_dir_contents_response,
                                     'Could not retrieve list of budgets')
        else:
            self.raise_exception(budget_dir_contents_response,
                                 'Could not retrieve list of budgets')

        # Need to replace (add, actually) UTC timezone to the naive datetime
        # returned by datetime.max, otherwise comparisons fail with a
        # TypeError when the strings are converted to datetime.
        earliest_iso8601_date = datetime.datetime.min.replace(
                tzinfo = dateutil.tz.tzutc()
        ).isoformat()

        # Build a dummy entry so max() can be used to maintain the newest
        # version of the budget.
        newest_budget_file = {'server_modified': earliest_iso8601_date}

        for entry in budget_dir_contents['entries']:
            if entry['.tag'] == 'file' and 'yfull' in entry['name']:
                logger.debug(
                    "Found budget file at {path}\n\tServer modification time: {date}"
                    .format(path=entry['path_lower'], date=entry['server_modified'])
                )
                newest_budget_file = max(
                    newest_budget_file,
                    entry,
                    key=lambda x: dateutil.parser.parse(x['server_modified'])
                )

        logger.debug("Using budget file at {budget_path}"
                     .format(budget_path=newest_budget_file))

        # If .tag does not exist then newest_budget_file is still the dummy
        # object and no budget file was found.
        if '.tag' not in newest_budget_file:
            error_msg = ('No budget file found for budget at "{path}"'
                        .format(path=budget_directory_path))
            logger.error(error_msg)
            raise Exception(error_msg)

        # The API call for downloading a file requires an empty or non-existent
        # Content-Type header. As it is set in the requests Session object,
        # clear it for this call.
        headers = {
            'Dropbox-API-Arg': json.dumps({'path': newest_budget_file['id']}),
            'Content-Type': None
        }

        start = time.clock()
        r = self.session.post(self.dropbox_endpoints['download'], headers=headers)
        end = time.clock()
        elapsed = end - start
        logger.debug("Dropbox API call time elapsed: {time}s, {speed} KB/s".format(time=elapsed, speed=(len(r.text) // 1024 // elapsed)))

        if r.status_code == requests.codes.ok:
            start = time.clock()
            budget_json = r.text.replace("\n", "")
            end = time.clock()
            elapsed = end - start
            logger.debug("Remove budget newlines time elapsed: {time}s, {speed} KB/s".format(time=elapsed, speed=(len(r.text) // 1024 // elapsed)))
            return budget_json
        else:
            self.raise_exception(r, 'Could not get the budget file')

