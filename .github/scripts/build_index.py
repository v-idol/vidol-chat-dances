from argparse import ArgumentParser
from pathlib import Path
import datetime
import json

import validate


def read_dance(file: Path):
    with open(file, 'r') as f:
        dance = json.load(f)
    for required_key in [
        "name",
        "url",
        "description",
    ]:
        assert required_key in dance, f"{file} missing key: {required_key}"

    try:
        datetime.date.fromisoformat(dance.get('created'))
    except:
        # add "created": "YYYY-MM-DD"
        dance["created"] = str(datetime.datetime.now().date())
        with open(file, 'w') as f:
            json.dump(dance, f, indent=4)
    return dance


def read_dance_dir():
    dance_list = {}
    for f in dance_dir.iterdir():
        if f.is_file() and f.suffix.lower() == '.json':
            dance = read_dance(f)
            dance_list[dance['url']] = dance
    return dance_list


def update_index(exts: dict):
    # update existing remove removed and add new dance
    with open(build_index_path, 'r') as f:
        existing_dance_list = {extension['url']: extension for extension in json.load(f)[
            'dance']}

    for dance_list_url, extension in exts.items():
        if dance_list_url in existing_dance_list.keys():
            existing_dance_list[dance_list_url].update(extension)
        else:
            existing_dance_list[dance_list_url] = extension
    dance_list_list = [extension for dance_list_url,
                   extension in existing_dance_list.items() if dance_list_url in dance_list]
    extension_index = {'dance_list': dance_list_list}

    with open(build_index_path, 'w') as f:
        json.dump(extension_index, f, indent=4)
    return extension_index


def update_main_index(index: dict):
    # add keys from main/index that are not in dance_list to dance_list as new main/index
    with open(deploy_index_path, 'r') as f:
        main_exts = {dance_list['url']: dance for dance in json.load(f)[
            'dance']}

    index_ext = {dance['url']: dance for dance in index['dance']}
    index_ext_urls = index_ext.keys()
    for main_ext_url, main_ext in main_exts.items():
        if main_ext_url in index_ext_urls:
            index_ext_keys = index_ext[main_ext_url].keys()
            for main_exts_key in main_ext.keys():
                if main_exts_key not in index_ext_keys:
                    index_ext[main_ext_url][main_exts_key] = main_ext[main_exts_key]

    new_main_index = {
        'dance': list(index_ext.values())}
    with open(deploy_index_path, 'w') as f:
        json.dump(new_main_index, f, indent=4)
    return new_main_index


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--build-branch", "-b", type=str,
                        default='', required=False)
    parser.add_argument("--deploy-branch", "-d", type=str,
                        default='', required=False)
    args = parser.parse_args()

    build_index_path = Path(args.build_branch).joinpath('index.json')
    deploy_index_path = Path(args.deploy_branch).joinpath('index.json')
    dance_dir = Path(args.build_branch).joinpath('dance')

    # read entries
    dance_list = read_dance_dir()

    # update indexs
    dance_index_ext = update_index(dance_list)
    dance_index_main = update_main_index(dance_index_ext)

    # validate
    validate.validate_index(build_index_path)
    validate.validate_index(deploy_index_path)

    assert len(dance_index_ext["dance"]) == len(dance_index_main["dance"]
                                                 ), f'entry count mismatch: {len(dance_index_ext["dance"])} {len(dance_index_main["dance"])}'
    print(
        f'::notice::{len(dance_index_ext["dance"])} dance')
