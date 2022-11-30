import random
import json
import adbutils
import typer
import os
import subprocess
from datetime import datetime
from droidbot.device import Device
from droidbot.app import App
import time

def check_and_create_dir(dir_name):
    if not os.path.exists(dir_name):
        # in case multiple directories need to be created. for example /activity_screenshots/appRelease
        os.makedirs(dir_name)


def unit_dynamic_testing(deviceId, apk_path, atg_json, ss_path, deeplinks_json, atg_save_dir, login_options,
                         log_save_path, test_time=1200, reinstall=False):
    visited_rate = []
    visited_activities = []
    # connect to device and install app
    isEmulator = False
    if deviceId.startswith("emulator"):
        isEmulator = True

    d = Device(
        device_serial=deviceId,
        is_emulator=isEmulator,
        output_dir=atg_save_dir,
        grant_perm=True
    )
    d.set_up()
    d.connect()


    # install app
    targetApp = App(apk_path, output_dir=atg_save_dir)
    d.install_app(targetApp)
    packageName = targetApp.package_name
    mainActivity = targetApp.main_activity

    test_start_time = datetime.now()

    # open app and get the screenshot of the first activity
    d.start_app(targetApp)
    time.sleep(2)
    d.take_screenshot()

    currentState = d.get_current_state()
    print(currentState)

    # save the json file
    stateJson = currentState.to_json()
    with open('test.json', 'w') as f:
        json.dump(stateJson, f)

    visited_activities.append(mainActivity)

    d.disconnect()



def dynamic_GUI_testing(emulator, app_name, outmost_directory, login_options, android_device, current_setting):
    current_directory = outmost_directory + "/guidedExplore/data"
    output_directory = outmost_directory + "/output/" + app_name + "/" + android_device + "/" + current_setting
    apk_path = current_directory + '/repackaged_apks/' + app_name + ".apk"
    check_and_create_dir(output_directory)
    atg_json = current_directory + "/" + app_name + '/activity_atg/' + app_name + ".json"
    atg_save_dir = current_directory + "/" + app_name + '/activity_atg/' + app_name + '_dynamic.json'
    # atg_json = current_directory + "/" + app_name + '/activity_atg.json'
    # atg_save_dir = current_directory + app_name + '/activity_atg_dynamic.json'
    ss_path = output_directory + '/activity_screenshots/'
    deeplinks_json = os.path.join(current_directory, app_name, 'deeplinks_params.json')
    log = current_directory + '/visited_rates/' + app_name + ".txt"
    check_and_create_dir(ss_path)
    check_and_create_dir(current_directory + '/visited_rates/')

    unit_dynamic_testing(emulator, apk_path, atg_json, ss_path, deeplinks_json, atg_save_dir, login_options, log,
                         reinstall=False)


if __name__ == '__main__':
    unit_dynamic_testing("08221FDD4004DF", "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/input/alltrails.apk",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/activity_atg/alltrails.json",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/output/alltrails/08221FDD4004DF/setting1/activity_screenshots/",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/deeplinks_params.json",
                         '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/',
                         'login_options', '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/visited_rates/alltrails.txt',)