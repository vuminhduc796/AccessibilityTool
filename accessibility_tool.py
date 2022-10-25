"""
This is an entry for Accessibility Tool
"""
import os
import threading
import time
from os.path import isfile, join
import typer
from pathlib import Path
import config.config as sys_config
import subprocess

from guidedExplore.dynamic_GUI_testing import dynamic_GUI_testing
from guidedExplore.run_preprocess import run_deer
from owleyes.cnn_cam3 import owleyes_scan
from xbot.code.run_xbot import run_xbot
from typing import List, Optional

app = typer.Typer(help="Android Accessibility Tool",no_args_is_help=True)
config_app = typer.Typer()
app.add_typer(config_app, name="config",help="Manage config.",no_args_is_help=True)
current_directory = os.getcwd()
cond = threading.Condition()
# export system variables
os.system("export ANDROID_SDK=" + sys_config.config_content["sdk_platform_path"])
print(sys_config.config_content["sdk_platform_path"])
print(os.system("export ANDROID_SDK_ROOT=" + sys_config.config_content["sdk_platform_path"]))

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

            #delete app
            cmd = "aapt dump badging %s | grep 'package' | awk -v FS=\"'\" '/package: name=/{print$2}'" % (
                        current_directory + "/input/ " + apk)
            defined_pkg_name = subprocess.getoutput(cmd)
            cmd = "adb -s " + device + " uninstall " + defined_pkg_name
            os.system(cmd)

            current_folder_device = apk_output_folder + "/" +  emulator_name_android_studio
            if not os.path.exists(current_folder_device):
                os.makedirs(current_folder_device)

            current_folder_setting = current_folder_device + "/" + current_setting
            if not os.path.exists(current_folder_setting):
                os.makedirs(current_folder_setting)

        # start threads
        thread_list = []
        if xbot or complete:
            xbot_thread = threading.Thread(target=xbot_thread_run, args=(
                apk, apk_output_folder, android_studio_devices, current_dark_mode, current_font_size))
            thread_list.append(xbot_thread)

        if uichecker or complete:
            ui_checker_thread = threading.Thread(target=ui_checker_thread_run, args=(apk_path, apk))
            thread_list.append(ui_checker_thread)

        if deer or screenshot_issue or complete:
            deer_thread = threading.Thread(target=deer_thread_run,
                                           args=(apk, devices_names, device_name_alias, current_setting))
            thread_list.append(deer_thread)

        if gcam or screenshot_issue or complete:
            owleyes_thread = threading.Thread(target=owleyes_thread_run, args=(
                devices_names, device_name_alias, apk_output_folder, current_setting))
            thread_list.append(owleyes_thread)

        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()

def xbot_thread_run(apk, apk_output_folder, android_studio_devices, current_dark_mode, current_font_size):
    # output folder for xbot
    with cond:
        # typer.secho("========Xbot========", fg=typer.colors.MAGENTA)
        if not os.path.exists(apk_output_folder):
            os.makedirs(apk_output_folder)
        # typer.secho("========Start running Xbot========", fg=typer.colors.MAGENTA)
        run_xbot(android_studio_devices, apk, current_directory, current_dark_mode, current_font_size)
        # typer.secho("========Xbot Finished========", fg=typer.colors.MAGENTA)
def ui_checker_thread_run(apk_path,apk):
    # typer.secho("========UI checker========", fg=typer.colors.MAGENTA)
    os.system(current_directory + "/uichecker/uicheck " + str(
        apk_path.absolute()) + "/" + apk + " " + current_directory + "/uichecker/rules/input.dl")
    # typer.secho("========UI checker Finished========", fg=typer.colors.MAGENTA)
def deer_thread_run(apk,devices_names,device_name_alias,current_setting):
    # deer
    # init login config
    with cond:
        # typer.secho("========deer========", fg=typer.colors.MAGENTA)
        login_options = {}
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
            dynamic_GUI_testing(device, apk[:-4], current_directory, login_options, emulator_name_android_studio,
                                current_setting)
            # deer
            # typer.secho("========Start running deer========", fg=typer.colors.MAGENTA)
        sys_config.inform_finish_deer()
            # typer.secho("========Deer Finished========", fg=typer.colors.MAGENTA)
def owleyes_thread_run(devices_names, device_name_alias, apk_output_folder, current_setting):
    with cond:
        for device in devices_names:
            emulator_name_android_studio = device_name_alias[device]["alias"]
            # typer.secho("========Start running owleye========", fg=typer.colors.MAGENTA)
            path = os.path.join(apk_output_folder, emulator_name_android_studio, current_setting)
            owleyes_scan(path, current_directory)
            # typer.secho("========OwlEye Finished========", fg=typer.colors.MAGENTA)
@app.command("replay")
def replay():
    """
    Replay bugs.
    """
    pass


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
    time.sleep(3)
    current_dark_mode = ""
    current_font_size = ""
    emulators = []
    for device in device_name_alias:
        emulator_name_android_studio = device_name_alias[device]["alias"]

        emulators.append(device)
        port_number = device[-4:]
        emulator_cmd = sys_config.config_content['sdk_platform_path'] + "/emulator/emulator"
        print(emulator_cmd)
        subprocess.Popen([emulator_cmd, "-port", port_number, '-avd', emulator_name_android_studio, "-no-snapshot-load"])

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


if __name__ == '__main__':
    app()
