import os

import typer
import yaml
from datetime import datetime
from uuid import uuid4
import json

config_path = os.getcwd() + '/config/config.yml'
config_json_path = os.getcwd() + '/config/config.json'
with open(config_path, 'r') as config:
    config_content = yaml.safe_load(config)
# initialization
config_content['updated'] = ''
config_content['finished'] = 'false'
with open(config_path, 'w') as w_f:
    yaml.dump(config_content, w_f)

# Data to be written
dictionary = {
    "app": {
    },
    "mode": "normal_light_mode",
}

# Serializing json
json_object = json.dumps(dictionary, indent=4)

# Writing to config.json
with open(config_json_path, "w") as outfile:
    outfile.write(json_object)


def add_emulator_config(key, value):
    config_content['emulators']['alias'][key] = value;
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def remove_emulator_config(key):
    try:
        config_content['emulators']['alias'].pop(key)
        with open(config_path, 'w') as w_f:
            yaml.dump(config_content, w_f)
    except:
        typer.secho("The emulator alias does not exist", fg=typer.colors.MAGENTA)


def add_auto_login_pass_config(username, password, activity, package_name):
    user_pass = {"method": "pass", 'username': username, 'password': password, 'activity': activity,
                 'packageName': package_name}
    config_content['auto-login'] = user_pass
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def add_auto_login_facebook_config(activity, package_name):
    user_pass = {'method': 'facebook', 'activity': activity, 'packageName': package_name}
    config_content['auto-login'] = user_pass
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def add_auto_login_facebook_default_config(username, password):
    user_pass = {'username': username, 'password': password}
    config_content['default_facebook'] = user_pass
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def remove_auto_login_config():
    config_content['auto-login'] = {'method': '', 'activity': '', 'packageName': ''}
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def initilize_config_for_deer(current_emulator, current_apk):
    if current_apk in dictionary['app'].keys():
        dictionary['app'][current_apk]['device'] = {
            current_emulator: {
                "activity": [],
                "isLoading": "",
                "isDone": "no"
            }
        }
    else:
        dictionary['app'][current_apk] = {
            "device": {
                current_emulator: {
                    "activity": [],
                    "isLoading": "",
                    "isDone": "no"
                }
            }
        }
    # Serializing json
    obj = json.dumps(dictionary, indent=4)

    # Writing to config.json
    with open(config_json_path, "w") as outfile:
        outfile.write(obj)


def inform_update_deer(current_emulator, current_apk, activity):
    if activity not in dictionary['app'][current_apk]['device'][current_emulator]['activity']:
        dictionary['app'][current_apk]['device'][current_emulator]['activity'].append(activity)
        dictionary['app'][current_apk]['device'][current_emulator]['isLoading'] = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        config_content['updated'] = dictionary['app'][current_apk]['device'][current_emulator]['isLoading']
        # Serializing json
        obj = json.dumps(dictionary, indent=4)
        # Writing to config.json
        with open(config_json_path, "w") as outfile:
            outfile.write(obj)
        # Writing to config.yml
        with open(config_path, 'w') as w_f:
            yaml.dump(config_content, w_f)


def inform_finish_deer(current_emulator, current_apk):
    dictionary['app'][current_apk]['device'][current_emulator]['isDone'] = 'yes'
    # Serializing json
    obj = json.dumps(dictionary, indent=4)
    # Writing to config.json
    with open(config_json_path, "w") as outfile:
        outfile.write(obj)
    config_content['finished'] = "true"
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)
