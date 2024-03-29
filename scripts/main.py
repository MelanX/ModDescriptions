import os
import subprocess
import sys

import requests

from util import get_data, get_default_slug

BASE_URL = 'https://raw.githubusercontent.com/MelanX/ModDescriptions/HEAD/'
MODRINTH_URL = 'https://modrinth.com/mod/'
CURSEFORGE_URL = 'https://www.curseforge.com/minecraft/mc-mods/'
DIR = 'assets/mods/'

MODRINTH_API = 'https://api.modrinth.com/v2/project/'

MODRINTH_TOKEN = sys.argv[1]


def update_logo(path, mod):
    logo = os.path.join(path, 'logo.png')
    if not os.path.exists(logo):
        print('Logo ❌')
        return

    # todo implement updating on Modrinth and CurseForge
    print('✔️ Logo')


def update_desc(path, mod):
    desc = os.path.join(path, 'desc.md')
    if not os.path.exists(desc):
        print('❌ Description')
        return

    with open(desc, 'r', encoding='utf-8') as f:
        content = f.read()

    content = important_information(content)

    print('🧾 Description')
    for image in os.listdir(path):
        if is_image(image):
            if image == 'promo.png':
                content += '\nYou are allowed to put this mod in any modpack you like.\n'
                content += f'![[Werbung](https://www.bisecthosting.com/melanx)]({image_url(path, image)})\n#Werbung #Ad'
                print('✔️ Promo')
                continue

            title = image.rsplit(".", 1)[0].replace("_", " ").title()
            old = content
            content = content.replace('{' + image + '}', f'![{title}]' +
                                                         f'({image_url(path, image)})')
            if old is not content:
                print(f'✔️ {title}')
    recipes = os.path.join(path, 'recipes')
    if os.path.exists(recipes):
        images_str = ''
        for recipe in os.listdir(recipes):
            images_str += f'**{recipe.split(".")[0].replace("_", " ").title()}**\n\n'
            images_str += f'![{recipe.rsplit(".", 1)[0].replace("_", " ").title()} Recipe]({image_url(recipes, recipe)})\n\n'
        content = content.replace('{recipe_images}', images_str)
        print('✔️ Example Recipes')

    print('✔️ Full Desc')
    update_modrinth_desc(mod, content)


def something_changed(path):
    with open('latest.txt', 'r', encoding='utf-8') as f:
        hash = f.readline().rstrip("\n")
        cmd = f'git diff --name-only {hash} -- {path} assets/important_notes.md'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        changed_files = result.stdout.decode().splitlines()

    return len(changed_files) > 0


def main():
    for mod in get_data()['projects']:
        slug = get_default_slug(mod)
        print(f'🔄️ Updating project pages for {mod["name"]}.')
        path = os.path.join(DIR, slug)
        if not os.path.exists(path):
            print(f'❌❌❌ No assets found. Skipping. ❌❌❌\n')
            continue

        if not something_changed(path):
            print('❌❌❌ No changes detected. Skipping. ❌❌❌\n')
            continue

        update_logo(path, mod)
        update_desc(path, mod)

        print(f'✔️ Finished {mod["name"]}\n')


def important_information(content: str):
    with open('assets/important_notes.md', 'r', encoding='utf-8') as f:
        data = f.read()

    if data.strip() != '':
        content = data + content

    return content


def is_image(file: str):
    return file.lower().endswith('.png') or file.lower().endswith('.gif')


def image_url(path, file):
    full_path = os.path.join(path, file).replace('\\', '/')
    if os.path.exists(full_path):
        return BASE_URL + str(full_path)

    if full_path.endswith('.png'):
        full_path = full_path[:len(full_path) - 3] + 'gif'
        if os.path.exists(full_path):
            return BASE_URL + full_path

    return None


def update_modrinth_desc(mod, content):
    if 'mr_id' not in mod:
        print('❌ Mod not available on Modrinth')
        return

    content = content.replace('{mod_hoster}', MODRINTH_URL, -1)
    url = MODRINTH_API + mod['mr_id']
    headers = {'Authorization': MODRINTH_TOKEN, 'Content-Type': 'application/json'}
    response = requests.patch(url, json={'body': content}, headers=headers)
    if response.status_code == 204:
        print('✔️ Successfully updated Modrinth description')
    else:
        print('❌ Error updating Modrinth description: ' + response.text)


if __name__ == '__main__':
    main()
