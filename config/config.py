import os

import typer
import yaml
from datetime import datetime
from uuid import uuid4

config_path = os.getcwd()+'/config/config.yml'
with open(config_path, 'r') as config:
    config_content = yaml.safe_load(config)
# initialization
config_content['updated'] = ''
config_content['finished'] = 'false'
with open(config_path, 'w') as w_f:
    yaml.dump(config_content, w_f)

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


def inform_update_deer():
    config_content['updated'] = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def inform_finish_deer():
    config_content['finished'] = "true"
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)
