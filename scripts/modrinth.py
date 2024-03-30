import os.path
import sys

import requests

MOD_PAGE = 'https://modrinth.com/mod/'
PROJECT_API = 'https://api.modrinth.com/v2/project/'
MODRINTH_TOKEN = sys.argv[1]


def exists_on_modrinth(mod):
    exists = 'mr_id' in mod

    if not exists:
        print('❌ Mod not available on Modrinth')

    return exists


def update_modrinth_desc(mod, content):
    if not exists_on_modrinth(mod):
        return

    content = content.replace('{mod_hoster}', MOD_PAGE, -1)
    url = PROJECT_API + mod['mr_id']
    headers = {'Authorization': MODRINTH_TOKEN, 'User-Agent': 'GitHub@MelanX/ModDescriptions', 'Content-Type': 'application/json'}
    response = requests.patch(url, json={'body': content}, headers=headers)
    if response.status_code == 204:
        print('✔️ Successfully updated Modrinth description')
    else:
        print('❌ Error updating Modrinth description: ' + response.text)


def update_modrinth_logo(logo, mod):
    if not exists_on_modrinth(mod):
        return

    data = open(logo, 'rb').read()
    if len(data) >= 262_144:
        print('❌ Logo too big, please compress')
        return

    file_type = os.path.splitext(logo)[1].lstrip('.')

    url = PROJECT_API + mod['mr_id'] + '/icon'
    params = {'ext': file_type}
    headers = {'Authorization': MODRINTH_TOKEN, 'User-Agent': 'GitHub@MelanX/ModDescriptions', 'Content-Type': 'image/' + file_type}

    response = requests.patch(url, params=params, data=data, headers=headers)

    if response.status_code == 204:
        print('✔️ Successfully updated Modrinth logo')
    else:
        print('❌ Error updating Modrinth logo: ' + response.text)
