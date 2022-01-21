'''
Client for gofile.io
'''

from hashlib import sha256

import requests

class Gofile:
    '''
    Client for gofile.io
    '''
    def __init__(self, token: str = None):
        '''
        Constructor.
        '''
        self.base_url = 'https://{}.gofile.io'
        if token is None:
            self.token = self.create_account()
        else:
            self.token = token

    # works
    def create_account(self) -> str:
        '''
        Create a new account.
        '''
        try:
            res = requests.get(f'{self.base_url.format("api")}/createAccount')
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']['token']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_server(self) -> str:
        '''
        Get the best server available to receive files.
        '''
        try:
            res = requests.get(f'{self.base_url.format("api")}/getServer')
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']['server']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def upload_file(self) -> dict:
        '''
        Upload one file on a specific server.
        If you specify a folderId, the file will be added to this folder.
        '''
        return {}

    # works
    def get_content(self, content_id: str, password: str = '') -> dict:
        '''
        Get a specific content details.
        '''
        params = {
            'contentId': content_id,
            'token': self.token,
            'websiteToken': 'websiteToken',
        }

        if password:
            try:
                digest = sha256(password.encode('utf-8')).hexdigest()
            except:
                raise SystemExit(f'failed to generate digest from password: {password}')
            params['password'] = digest
        
        try:
            res = requests.get(f'{self.base_url.format("api")}/getContent', params=params)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def create_folder(self) -> None:
        '''
        Create a new folder.
        '''
        return

    def set_folder_option(self) -> None:
        '''
        Set an option on a folder.
        '''
        return

    def copy_content(self) -> None:
        '''
        Copy one of multiple contents to another folder.
        '''
        return

    def delete_content(self) -> None:
        '''
        Delete one or multiple files/folders.
        '''
        return

    def get_account_details(self) -> dict:
        '''
        Retrieving specific account information.
        '''
        return {}

    def upload(self, file):
        '''
        Upload a file to gofile.io
        '''
        import requests
        import os
        import json
        files = {'file': (os.path.basename(file), open(file, 'rb'))}
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.post(self.base_url + 'upload', files=files, headers=headers)
        if r.status_code == 200:
            return json.loads(r.text)['url']
        else:
            return None

    def delete(self, url):
        '''
        Delete a file from gofile.io
        '''
        import requests
        import json
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(self.base_url + url, headers=headers)
        if r.status_code == 200:
            return json.loads(r.text)['url']
        else:
            return None
