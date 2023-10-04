from argparse import ArgumentParser
from pathlib import Path
import datetime
import json

import validate


def read_agent(file: Path):
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


def read_agent_dir():
    dances = {}
    for f in agents_dir.iterdir():
        if f.is_file() and f.suffix.lower() == '.json':
            dance = read_agent(f)
            dances[dance['url']] = dance
    return dances


def update_index(exts: dict):
    # update existing remove removed and add new dances
    with open(build_index_path, 'r') as f:
        existing_agents = {extension['url']: extension for extension in json.load(f)[
            'dances']}

    for agents_url, extension in exts.items():
        if agents_url in existing_agents.keys():
            existing_agents[agents_url].update(extension)
        else:
            existing_agents[agents_url] = extension
    agents_list = [extension for agents_url,
                   extension in existing_agents.items() if agents_url in dances]
    extension_index = {'dances': agents_list}

    with open(build_index_path, 'w') as f:
        json.dump(extension_index, f, indent=4)
    return extension_index


def update_main_index(index: dict):
    # add keys from main/index that are not in dances to dances as new main/index
    with open(deploy_index_path, 'r') as f:
        main_exts = {dance['url']: dance for dance in json.load(f)[
            'dances']}

    index_ext = {dance['url']: dance for dance in index['dances']}
    index_ext_urls = index_ext.keys()
    for main_ext_url, main_ext in main_exts.items():
        if main_ext_url in index_ext_urls:
            index_ext_keys = index_ext[main_ext_url].keys()
            for main_exts_key in main_ext.keys():
                if main_exts_key not in index_ext_keys:
                    index_ext[main_ext_url][main_exts_key] = main_ext[main_exts_key]

    new_main_index = {
        'dances': list(index_ext.values())}
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
    agents_dir = Path(args.build_branch).joinpath('dances')

    # read entries
    dances = read_agent_dir()

    # update indexs
    agent_index_ext = update_index(dances)
    agent_index_main = update_main_index(agent_index_ext)

    # validate
    validate.validate_index(build_index_path)
    validate.validate_index(deploy_index_path)

    assert len(agent_index_ext["dances"]) == len(agent_index_main["dances"]
                                                 ), f'entry count mismatch: {len(agent_index_ext["dances"])} {len(agent_index_main["dances"])}'
    print(
        f'::notice::{len(agent_index_ext["dances"])} dances')
