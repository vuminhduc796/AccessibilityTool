import typer
import yaml

config_path = './config/config.yml'
with open(config_path, 'r') as config:
    config_content = yaml.safe_load(config)


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


def add_auto_login_config(apk, username, password):
    user_pass= {'username':username,'password': password}
    config_content['auto-login'][apk]=user_pass
    with open(config_path, 'w') as w_f:
        yaml.dump(config_content, w_f)


def remove_auto_login_config(apk):
    try:
        config_content['auto-login'].pop(apk)
        with open(config_path, 'w') as w_f:
            yaml.dump(config_content, w_f)
    except:
        typer.secho("The setting for apk " + apk + " does not exist", fg=typer.colors.MAGENTA)
