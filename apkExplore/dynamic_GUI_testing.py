import random
import json
from os.path import isfile, join

import adbutils
import typer
import os
import subprocess
from datetime import datetime

from apkExplore.droidbot.intent import Intent
from apkExplore.xbot_kit import scan_and_return, collect_results
from droidbot.device import Device
from droidbot.app import App
import time


def check_and_create_dir(dir_name):
    if not os.path.exists(dir_name):
        # in case multiple directories need to be created. for example /activity_screenshots/appRelease
        os.makedirs(dir_name)


def run_xbot_check(activity, accessibility_path, deviceId, appName):
    scan_and_return(deviceId)
    collect_results(activity, accessibility_path, deviceId, appName)


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
    isAppOpened = d.install_app(targetApp)
    packageName = targetApp.package_name
    mainActivity = targetApp.main_activity

    test_start_time = datetime.now()

    numberOfActivities = 0
    numberOfSuccessful = 0
    # open app and get the screenshot of the first activity
    currentState = d.get_current_state()
    if isAppOpened:
        d.start_app(targetApp)
        time.sleep(2)
        with open(deeplinks_json, 'r', encoding='utf8') as f:
            activities = json.loads(f.read())
            for activity in activities:
                numberOfActivities += 1
                for deeplink in activities[activity]:
                    intent = Intent(component=deeplink["component"],
                                    action=deeplink["action"],
                                    category=deeplink["category"],
                                    extra_boolean=deeplink["extra_boolean"],
                                    extra_int=deeplink["extra_int"],
                                    data_uri=deeplink["data_uri"],
                                    extra_keys=deeplink["extra_keys"],
                                    extra_array_float=deeplink["extra_array_float"],
                                    extra_array_long=deeplink["extra_array_long"],
                                    extra_array_int=deeplink["extra_array_int"],
                                    extra_float=deeplink["extra_float"],
                                    extra_long=deeplink["extra_long"],
                                    extra_component=deeplink["extra_component"],
                                    extra_string=deeplink["extra_string"],
                                    )

                    time.sleep(2)
                    try:
                        d.send_intent(intent=intent.get_cmd())
                    except subprocess.CalledProcessError as e:
                        print("Ping stdout output:\n", e.output)
                    time.sleep(3)
                    print(intent.__str__())
                    currentScreen = d.get_top_activity_name().split("/")[-1]
                    print("current: " + currentScreen)
                    print("desire: " + activity)
                    if currentScreen in activity:
                        print("activity explored - break condition")
                        numberOfSuccessful += 1
                        d.go_home()
                        break
                    d.go_home()
                    time.sleep(1)

                print("total: " + numberOfActivities.__str__() + ", success: " + numberOfSuccessful.__str__())

    # print(currentState.views)

    # save the json file
    stateJson = currentState.to_json()
    with open('test.json', 'w') as f:
        json.dump(stateJson, f)

    visited_activities.append(mainActivity)

    d.disconnect()


def dynamic_GUI_testing(emulator, app_name, outmost_directory, login_options, android_device, current_setting):
    current_directory = outmost_directory + "/guidedExplore/data"
    output_directory = outmost_directory + "/output/" + app_name + "/" + android_device + "/" + current_setting
    apk_path = outmost_directory + '/input/' + app_name + ".apk"
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
    # unit_dynamic_testing("08221FDD4004DF", "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/input/alltrails.apk",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/activity_atg/alltrails.json",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/output/alltrails/08221FDD4004DF/setting1/activity_screenshots/",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/deeplinks_params.json",
    #                      '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/',
    #                      'login_options', '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/visited_rates/alltrails.txt',)
    print(os.getcwd())
    outmost_directory = os.getcwd().replace('/apkExplore', '')
    #
    # run_deer(apk_file, emulator, outmost_directory)
    apks = [f for f in os.listdir("../input") if isfile(join(outmost_directory + "/input", f))]
    excluded_apps = ["Telegram.apk","AliExpress.apk","Wildberries.apk","VidMate.apk"]
    # for apk in apks:
    #     if apk not in excluded_apps:
    #         dynamic_GUI_testing("emulator-5554", apk[:-4], outmost_directory, False, "phone-vertical",
    #                            "normal")
    dynamic_GUI_testing("emulator-5554", "MicrosoftEdge", os.getcwd().replace("/apkExplore", ""), False, "phone-vertical", "normal")
