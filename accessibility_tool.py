"""
This is an entry for Accessibility Tool
"""
import os
import threading
import time
from os.path import isfile, join
import typer
from pathlib import Path

import app_utils
import config.config as sys_config
import subprocess
import shutil

from apkExplore.dynamic_GUI_testing import dynamic_GUI_testing
from guidedExplore.run_preprocess import run_deer
from owleyes.cnn_cam3 import owleyes_scan
from typing import List, Optional




app = typer.Typer(help="Android Accessibility Tool", no_args_is_help=True)
config_app = typer.Typer()
app.add_typer(config_app, name="config", help="Manage config.", no_args_is_help=True)
emulator_app = typer.Typer()
app.add_typer(emulator_app, name="emulator",help="Manage emulators.",no_args_is_help=True)
current_directory = os.getcwd()
cond = threading.Condition()
sdk = sys_config.config_content["sdk_platform_path"]
adb = sdk + '/platform-tools/adb'
avdmanager = sdk + "/tools/bin/avdmanager"
sdkmanager = sdk + "/tools/bin/sdkmanager"
emulator = sdk + "/emulator/emulator"

# export system variables
os.system("export ANDROID_SDK=" + sys_config.config_content["sdk_platform_path"])
os.system("export ANDROID_SDK_ROOT=" + sys_config.config_content["sdk_platform_path"])


def delete_auto_login_config(remove_auto_login: bool):
    if remove_auto_login:
        sys_config.remove_auto_login_config()


@app.command("detect")
def detect_file_availability_issues(

        apk_path: Path = typer.Option(current_directory + '/input', "--input", "--i",
                                      exists=True,
                                      file_okay=False,
                                      dir_okay=True,
                                      writable=False,
                                      readable=True,
                                      help="The path of files that are being detected"
                                      ),
        devices: Optional[List[str]] = typer.Option(sys_config.config_content["emulators"]["default"], "--device",
                                                    "--d", help="Uses device to test accessibility issues"),
        xbot: bool = typer.Option(False, "--scan", help="Uses Xbot to scan to generate screenshots."),
        uichecker: bool = typer.Option(False, "--ui", "--u", help="Uses UI Checker to generate accessibility "
                                                                  "report of UI in json format"),
        # deer: bool = typer.Option(False, "--graph", "--g", help="Uses Deer to form transition graphs"),
        deer: bool = typer.Option(False, "--screenshot", "--s", help="Uses OwlEye to generate screenshots of errors"),
        screenshot_issue: bool = typer.Option(False, "--screenshot_issue", "--s",
                                              help="Uses OwlEye to generate screenshots of errors"),
        gcam: bool = typer.Option(False, "--gcam", "--gc",
                                  help="Uses OwlEye to generate screenshots of errors"),
        complete: bool = typer.Option(False, "--all", "--a", help="Uses all the tools(Xbot, UI checker, deer and "
                                                                  "OwlEye)")
):
    """
    Detect Accessibility issues.
    """

    # check options
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    if not complete and not xbot and not uichecker and not deer and not screenshot_issue and not gcam and not complete:
        typer.secho("Please select at least one tool to detect.", fg=typer.colors.MAGENTA)
        exit()
    # replace devices with their real names
    devices_names = []
    device_name_alias = {}
    for device in devices:

        if device in sys_config.config_content['emulators']['alias']:
            device_name_alias[sys_config.config_content['emulators']['alias'][device]] = {'alias': device}
            devices_names.append(sys_config.config_content['emulators']['alias'][device])
        else:
            devices_names.append(device)

    apks = [f for f in os.listdir(apk_path) if isfile(join(current_directory + "/input", f))]

    for apk in apks:

        apk_output_folder = current_directory + "/output/" + apk[:-4]
        # set up emulators
        if deer or screenshot_issue or complete or xbot:
            android_studio_devices, current_dark_mode, current_font_size = set_up_devices(device_name_alias)
        else:
            current_font_size = sys_config.config_content["font_size"]
            if sys_config.config_content["dark_mode"] == "true":
                current_dark_mode = "dark_mode"
            else:
                current_dark_mode = "light_mode"
        # for naming output folder
        current_setting = current_font_size + "_" + current_dark_mode
        # create output folder
        if not os.path.exists(apk_output_folder):
            os.makedirs(apk_output_folder)

        for device in device_name_alias:

            emulator_name_android_studio = device_name_alias[device]["alias"]

            # delete app
            cmd = "aapt dump badging %s | grep 'package' | awk -v FS=\"'\" '/package: name=/{print$2}'" % (
                    current_directory + "/input/ " + apk)
            defined_pkg_name = subprocess.getoutput(cmd)
            cmd = "adb -s " + device + " uninstall " + defined_pkg_name
            os.system(cmd)

            current_folder_device = apk_output_folder + "/" + emulator_name_android_studio
            if not os.path.exists(current_folder_device):
                os.makedirs(current_folder_device)

            current_folder_setting = current_folder_device + "/" + current_setting
            if not os.path.exists(current_folder_setting):
                os.makedirs(current_folder_setting)

        # start threads
        thread_list = []

        timer1 = RepeatTimer(10, app_utils.sync_front_end_data)
        timer1.start()

        # timer2 = RepeatTimer(10, owleyes_thread_run,[devices_names, device_name_alias, apk_output_folder, current_setting])
        # timer2.start()

        front_end_thread = threading.Thread(target=front_end_run)
        thread_list.append(front_end_thread)

        if uichecker or complete:
            ui_checker_thread = threading.Thread(target=ui_checker_thread_run, args=(apk_path, apk))
            thread_list.append(ui_checker_thread)

        if deer or screenshot_issue or complete:
            deer_thread = threading.Thread(target=deer_thread_run,
                                           args=(apk, devices_names, device_name_alias, current_setting))
            thread_list.append(deer_thread)

        # if gcam or screenshot_issue or complete:
        #     owleyes_thread = threading.Thread(target=owleyes_thread_run, args=(
        #         devices_names, device_name_alias, apk_output_folder, current_setting))
        #     thread_list.append(owleyes_thread)

        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()


def front_end_run():
    # start frontend
    start_front_end_cmd = "cd frontend && npm start"
    p = subprocess.run(start_front_end_cmd, shell=True)


def ui_checker_thread_run(apk_path, apk):
    # typer.secho("========UI checker========", fg=typer.colors.MAGENTA)
    os.system(current_directory + "/uichecker/uicheck " + str(
        apk_path.absolute()) + "/" + apk + " " + current_directory + "/uichecker/rules/input.dl")
    # typer.secho("========UI checker Finished========", fg=typer.colors.MAGENTA)


def deer_thread_run(apk, devices_names, device_name_alias, current_setting):
    # deer
    # init login config
    with cond:
        # typer.secho("========deer========", fg=typer.colors.MAGENTA)
        login_options = {
            'hasLogin': False,
            'facebookLogin': False,
            'username': '',
            'password': '',
            'activityName': '',
            'packageName': '',
        }
        if "auto-login" in sys_config.config_content:
            if sys_config.config_content["auto-login"]['method'] == 'facebook':
                login_options = {
                    'username': sys_config.config_content["default_facebook"]['username'],
                    'password': sys_config.config_content["default_facebook"]['password'],
                    'activityName': sys_config.config_content["auto-login"]['activity'],
                    'packageName': sys_config.config_content["auto-login"]['packageName'],
                    'hasLogin': False,
                    'facebookLogin': True
                }
            else:
                login_options = {
                    'username': sys_config.config_content["auto-login"]['username'],
                    'password': sys_config.config_content["auto-login"]['password'],
                    'activityName': sys_config.config_content["auto-login"]['activity'],
                    'packageName': sys_config.config_content["auto-login"]['packageName'],
                    'hasLogin': True,
                    'facebookLogin': False
                }

        # run_deer(apk, current_directory, login_options)
        run_deer(apk, current_directory)
        # run for each device
        for device in devices_names:
            # get device name from number
            emulator_name_android_studio = device_name_alias[device]["alias"]
            app_name = apk[:-4]
            app_utils.add_new_config(app_name, emulator_name_android_studio, current_setting)
            dynamic_GUI_testing(device, app_name, current_directory, login_options, emulator_name_android_studio,
                                current_setting)
            # deer
            # typer.secho("========Start running deer========", fg=typer.colors.MAGENTA)
        sys_config.inform_finish_deer()
        # typer.secho("========Deer Finished========", fg=typer.colors.MAGENTA)


# def owleyes_thread_run(devices_names, device_name_alias, apk_output_folder, current_setting):
#     for device in devices_names:
#         emulator_name_android_studio = device_name_alias[device]["alias"]
#         # typer.secho("========Start running owleye========", fg=typer.colors.MAGENTA)
#         path = os.path.join(apk_output_folder, emulator_name_android_studio, current_setting)
#         owleyes_scan(path, current_directory)
#         # typer.secho("========OwlEye Finished========", fg=typer.colors.MAGENTA)


@app.command("replay")
def replay():
    """
    Replay bugs.
    """
    pass

@emulator_app.command("default")
def create_default_emulators(tablet: bool = typer.Option(False, "--tablet", "-t", help="Create tablet emulators")):
    """
        Create default emulators.
    """
    # delete previous AVDs
    try:
        os.system(avdmanager + " delete avd -n phone-vertical")
        os.system(avdmanager + " delete avd -n phone-horizontal")
        if tablet:
            os.system(avdmanager + " delete avd -n tablet-vertical")
            os.system(avdmanager + " delete avd -n tablet-horizontal")
    except Exception as e:
        print(e)

    # setup new AVDs
    emulator_setup("phone-horizontal", "pixel_xl", True, tablet)
    emulator_setup("phone-vertical", "pixel_xl", False, tablet)
    if tablet:
        emulator_setup("tablet-horizontal", "pixel_c", True, tablet)
        emulator_setup("tablet-vertical", "pixel_c", False, tablet)

@emulator_app.command("devices")
def view_devices():
    """
    View available devices
    """
    os.system(avdmanager + " list device")

@emulator_app.command("view")
def view_emulators():
    """
    View created emulators
    """
    os.system(avdmanager + " list avd")

@emulator_app.command("delete")
def view_emulators(emulator_names: List[str] = typer.Argument(..., help="List of names of the emulators to delete")):
    """
    Delete existing emulator
    """
    for name in emulator_names:
        os.system(avdmanager + " delete avd -n " + name)

@emulator_app.command("create")
def create_emulator(name: str = typer.Option(..., "--name", "-n", help="Name of the emulator"),
                    device: str = typer.Option("pixel_xl", "--device", "-d", help="Device index or id"),
                    horizontal: bool = typer.Option(False, "--horizontal", "-h", help="Create the horizontal device"),
                    tablet: bool = typer.Option(False, "--tablet", "-t", help="Create tablet emulator")):
    """
    Create emulator
    """
    emulator_setup(name, device, horizontal, tablet)

@emulator_app.command("snapshot_save")
def snapshot_save(name: str = typer.Option(..., "--name", "-n", help="Name of the snapshot"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Save snapshot and store in emulator
    """
    if serial:
        serial = ' -s ' + serial
    os.system(f'{adb}{serial} emu avd snapshot save {name}')


@emulator_app.command("snapshot_load")
def snapshot_save(name: str = typer.Option(..., "--name", "-n", help="Name of the snapshot"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Load snapshot stored in emulator
    """
    if serial:
        serial = ' -s ' + serial
    os.system(f'{adb}{serial} emu avd snapshot load {name}')

@emulator_app.command("snapshot_export")
def snapshot_save(name: str = typer.Option(..., "--name", "-n", help="Name of the snapshot"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Export snapshot from emulator to /snapshots
    """
    if serial:
        serial = ' -s ' + serial
    path = os.getcwd() + "/snapshots/" + name
    os.system(f'{adb}{serial} emu avd snapshot pull {name} {path}')

@emulator_app.command("snapshot_import")
def snapshot_save(name: str = typer.Option(..., "--name", "-n", help="Name of the snapshot"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Import snapshot from /snapshots to emulator
    """
    if serial:
        serial = ' -s ' + serial
    path = os.getcwd() + "/snapshots/" + name
    os.system(f'{adb}{serial} emu avd snapshot push {name} {path}')

@emulator_app.command("font_size")
def snapshot_save(value: str = typer.Option(..., "--value", "-v", help="Value to set as the font size"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Set the font size
    """
    if serial:
        serial = ' -s ' + serial
    os.system(f'{adb}{serial} shell settings put system font_scale {value}')

@emulator_app.command("screen_size")
def snapshot_save(value: str = typer.Option(..., "--value", "-v", help="Value to set as the font size"),
                  serial: str = typer.Option("", "--serial", "-s", help="emulator serial number. e.g. emulator-5554. Can be left blank if there is only one emulator running")):
    """
    Set the screen size
    """
    if serial:
        serial = ' -s ' + serial
    os.system(f'{adb}{serial} shell wm size {value}')

@emulator_app.command("running")
def snapshot_save():
    """
    View running emulator serial numbers
    """
    os.system(adb + ' devices')


def emulator_setup(name, device, horizontal, tablet):
    if sys_config.config_content["arm64"] == 'true':
        package = "system-images;android-28;default;arm64-v8a"
    else:
        package = "system-images;android-28;default;x86"

    os.system(sdkmanager + f' "{package}"')
    os.system(avdmanager + f' create avd -n {name} -k "{package}" -d {device}')
    os.system(emulator + f' -avd {name} -port 5584 &')  # start the emulator

    time.sleep(1)
    os.system(adb + ' -s emulator-5584 wait-for-device')
    while subprocess.check_output(adb + ' -s emulator-5584 shell getprop sys.boot_completed', shell=True, text=True).strip() != "1":
        time.sleep(1)

    # install scanner apk
    scanner_apk = os.getcwd() + "/xbot/scanner.apk"
    os.system(adb + ' -s emulator-5584 install ' + scanner_apk)

    os.system(adb + " -s emulator-5584 shell settings put system font_scale 1.0")  # set font size to 1
    if (horizontal and not tablet) or (not horizontal and tablet):
        os.system(adb + " shell settings put system accelerometer_rotation 0")
        os.system(adb + " shell settings put system user_rotation 3")

    time.sleep(1)
    os.system(adb + " -s emulator-5584 emu kill")  # kill the emulator
    time.sleep(5)

@config_app.command("emulator")
def emulator_config(add_emulator: Optional[List[str]] = typer.Option(None, "--add",
                                                                     "--a",
                                                                     help="Format:[alias:name], adds an [alias] for "
                                                                          "the emulator [name]"),
                    remove_emulator: Optional[List[str]] = typer.Option(None, "--delete",
                                                                        "--d",
                                                                        help="Format:[alias], delete an [alias]")
                    ):
    """
    Set up Android emulators for testing App Accessibility.
    """
    for emulator in add_emulator:
        if (not ':' in emulator):
            typer.secho("incorrect format:[alias:name]", fg=typer.colors.MAGENTA)
        else:
            emulator_key_value = emulator.split(':')
            emulator_alias = emulator_key_value[0]
            emulator_name = emulator_key_value[1]
            sys_config.add_emulator_config(emulator_alias, emulator_name)
    for emulator in remove_emulator:
        sys_config.remove_emulator_config(emulator)


@config_app.command("auto_login")
def auto_login(pass_login: str = typer.Option(None, "--pass",
                                              "--p",
                                              help="Format:[username:password:activity"
                                                   ":package_name], set up ["
                                                   "username] "
                                                   ", [password], [activity] and [package_name] "
                                                   "for the apk in the config file."),
               facebook_login: str = typer.Option(None, "--facebook",
                                                  "--f",
                                                  help="Format:[activity"
                                                       ":package_name], set up [activity] and [package_name] "
                                                       "for the apk in the config file."),
               default_facebook_user_pass: str = typer.Option(None, "--setting",
                                                              help="Format:[username"
                                                                   ":password], set up default [username] and ["
                                                                   "password] "
                                                                   "for loging in to the facebook."),

               remove_auto_login: Optional[bool] = typer.Option(
                   None, "--delete", '--d', callback=delete_auto_login_config,
                   help="Deletes auto-login configs."),
               ):
    """
    Set up User credentials and apk information for auto login.
    """
    if pass_login:
        formatted_user_pass = pass_login.split(":")
        sys_config.add_auto_login_pass_config(formatted_user_pass[0], formatted_user_pass[1], formatted_user_pass[2],
                                              formatted_user_pass[3])
    if facebook_login:
        formatted_facebook_config = facebook_login.split(":")
        sys_config.add_auto_login_facebook_config(formatted_facebook_config[0], formatted_facebook_config[1])
    if default_facebook_user_pass:
        formatted_facebook_default_config = default_facebook_user_pass.split(":")
        sys_config.add_auto_login_facebook_default_config(formatted_facebook_default_config[0],
                                                          formatted_facebook_default_config[1])


def set_up_devices(device_name_alias):
    os.system("adb kill-server")
    os.system("adb start-server")
    os.system("adb -s emulator-5556 emu kill")
    os.system("adb -s emulator-5558 emu kill")
    os.system("adb -s emulator-5560 emu kill")
    os.system("adb -s emulator-5554 emu kill")
    time.sleep(5)
    current_dark_mode = ""
    current_font_size = ""
    emulators = []
    for device in device_name_alias:
        emulator_name_android_studio = device_name_alias[device]["alias"]

        emulators.append(device)
        port_number = device[-4:]
        emulator_cmd = sys_config.config_content['sdk_platform_path'] + "/emulator/emulator"
        print(emulator_cmd)
        subprocess.Popen(
            [emulator_cmd, "-port", port_number, '-avd', emulator_name_android_studio, "-no-snapshot-load"])

    time.sleep(10)

    for emulator in emulators:
        adb = "adb -s %s" % (emulator)
        os.system(adb + " root")

        # setting dark mode
        if sys_config.config_content["dark_mode"] == "true":
            os.system(adb + " shell settings put secure ui_night_mode 2")
            current_dark_mode = "dark_mode"
        else:
            os.system(adb + " shell settings put secure ui_night_mode 1")
            current_dark_mode = "light_mode"

        # setting font size
        current_font_size = sys_config.config_content["font_size"]
        if current_font_size == "small":
            os.system(adb + " shell settings put system font_scale 0.85")
        elif current_font_size == "large":
            os.system(adb + " shell settings put system font_scale 1.15")
        elif current_font_size == "extra_large":
            os.system(adb + " shell settings put system font_scale 1.30")
        else:
            os.system(adb + " shell settings put system font_scale 1.0")
    return emulators, current_dark_mode, current_font_size


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    app()
