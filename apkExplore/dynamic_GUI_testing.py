import random
import json
from os.path import isfile, join

import os
import subprocess
from datetime import datetime
from apkExplore.droidbot.exploration.Graph import Graph, Screen, Edge
from apkExplore.droidbot.intent import Intent
from apkExplore.xbot_kit import scan_and_return, collect_results
from droidbot.device import Device, dict_hash_current_screen
from droidbot.app import App
import time


def check_and_create_dir(dir_name):
    if not os.path.exists(dir_name):
        # in case multiple directories need to be created. for example /activity_screenshots/appRelease
        os.makedirs(dir_name)


def email_password_login(d, login_options):
    # d.app_start('com.alltrails.alltrails', '.ui.authentication.mediaauth.AuthActivity')

    # adbArgs = ['am', 'start', '-n', login_options['packageName'] + '/' + login_options['activityName']]
    # d.adb.shell(adbArgs)
    # TODO: save the current activity

    time.sleep(3)
    currentState = d.get_current_state()
    targetView = currentState.get_view_with_keywords('already have an account')
    if targetView is None:
        targetView = currentState.get_view_with_keywords('log in')
    if targetView is None:
        targetView = currentState.get_view_with_keywords('sign in')
    if targetView is not None:
        x, y = currentState.get_view_center(targetView)
        d.view_touch(x, y)
        time.sleep(5)
        print('clicked login button')

    currentState = d.get_current_state()

    #     try to input username and password
    usernameView = currentState.get_input_view_with_keywords('email')
    if usernameView is None:
        usernameView = currentState.get_input_view_with_keywords('username')
    if usernameView is not None:
        x, y = currentState.get_view_center(usernameView)
        d.view_touch(x, y)
        d.view_set_text(login_options['username'])
        time.sleep(5)
        d.key_press('BACK')
        time.sleep(5)

    currentState = d.get_current_state()

    passwordView = currentState.get_input_view_with_keywords('password')
    if passwordView is not None:
        x, y = currentState.get_view_center(passwordView)
        print(passwordView)
        d.view_touch(x, y)
        d.view_set_text(login_options['password'])
        time.sleep(5)
        d.key_press('BACK')
        time.sleep(5)

    currentState = d.get_current_state()

    # click login button
    loginView = currentState.get_view_with_keywords('log in')
    if loginView is None:
        loginView = currentState.get_view_with_keywords('sign in')
    if loginView is not None:
        print(loginView)
        x, y = currentState.get_view_center(loginView)
        d.view_touch(x, y)
        time.sleep(5)

    # except Exception as e:
    #
    #     print('Failed to start {} because {}'.format(login_options['activityName'], e))
    #     return False

    return True


def login_with_facebook(d, login_options):
    # d.app_start('com.alltrails.alltrails', '.ui.authentication.mediaauth.AuthActivity')
    try:

        # d.app_start(login_options['packageName'], login_options['activityName'])
        adbArgs = ['am', 'start', '-n', login_options['packageName'] + '/' + login_options['activityName']]
        d.adb.shell(adbArgs)

        time.sleep(3)
        currentState = d.get_current_state()
        # TODO: save the current activity

        # check facebookLogin
        elementId = currentState.get_view_with_keywords('facebook')
        if elementId is None:
            return False
        if elementId is not None:
            x, y = currentState.get_view_center(elementId)
            d.view_touch(x, y)
            time.sleep(15)

        #     try to input username and password
        currentState = d.get_current_state()

        #
        passwordTextEdit = currentState.get_input_view_with_keywords('password')
        if passwordTextEdit is not None:
            x, y = currentState.get_view_center(passwordTextEdit)
            d.view_touch(x, y)
            d.view_set_text(login_options['password'])
            d.key_press('BACK')
            time.sleep(5)

            usernameTextEdit = currentState.get_input_view_with_keywords('email')
            if usernameTextEdit is None:
                usernameTextEdit = currentState.get_input_view_with_keywords('username')
            if usernameTextEdit is not None:
                x, y = currentState.get_view_center(usernameTextEdit)
                d.view_touch(x, y)
                d.view_set_text(login_options['username'])
                d.key_press('BACK')
                time.sleep(4)
                loginElement = currentState.get_view_with_keywords('log in')
                if loginElement is not None:
                    x, y = currentState.get_view_center(loginElement)
                    d.view_touch(x, y)
                    time.sleep(5)

        # click continue button
        currentState = d.get_current_state()
        elementView = currentState.get_view_with_keywords('continue')
        if elementView is not None:
            x, y = currentState.get_view_center(elementView)
            d.view_touch(x, y)
            time.sleep(5)


    except Exception as e:

        print('Failed to start {} because {}'.format(login_options['activityName'], e))
        return False

    return True


def run_xbot_check(activity, output_dir, device):
    scan_and_return(device.serial)
    collect_results(activity, output_dir, device)


def unit_dynamic_testing(deviceId, apk_path, atg_json, output_dir, deeplinks_json, atg_save_dir, login_options,
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
    buttons_by_screen_hash = {}
    graph = Graph()
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


                    views = d.get_views()
                    print("desire: " + activity)

                    # if login_options['hasLogin']:
                    #     print("login")
                    #     email_password_login(d, login_options)
                    #
                    # if login_options['facebookLogin']:
                    #     login_with_facebook(d, login_options)
                    # print(clickable_views)
                    currentScreen = d.get_top_activity_name().split("/")[-1]
                    if currentScreen in activity:
                        t_end = time.time() + 120
                        start_exploration(activity, d, graph, output_dir,"", "", t_end)
                        numberOfSuccessful += 1


                        time.sleep(2)
                        d.go_home()
                        break
                    d.go_home()
                    time.sleep(1)

                print("total: " + numberOfActivities.__str__() + ", success: " + numberOfSuccessful.__str__())

    # print(currentState.views)
    # try automatic login

    currentState = d.get_current_state()
    print(currentState)

    # save the json file
    stateJson = currentState.to_json()
    with open('test.json', 'w') as f:
        json.dump(stateJson, f)

    visited_activities.append(mainActivity)

    d.disconnect()


def start_exploration(activity, d, graph, output_dir, previous_view_hash, clicked_btn, t_end):
    if time.time() > t_end:
        print("time is up")
        return
    currentScreenTree = d.get_top_activity_name().split("/")[-1]
    views = d.get_views()
    currentActivity = d.get_top_activity_name().split("/")[-1]
    currentScreenHash = dict_hash_current_screen(views)
    print(d.get_top_activity_name())
    # print(views)
    if currentActivity in "com.android.launcher3/.Launcher":
        return
    if currentActivity not in activity:
        d.key_press('BACK')
    if previous_view_hash != currentScreenHash:
        newEdge = Edge(clicked_btn, previous_view_hash,currentScreenHash)
        graph.addEdge(newEdge)
    clickable_views = []
    # print(views)
    if views is not None:
        for view in views:
            if view["clickable"] is True:
                clickable_views.append(view)
    if not graph.checkScreenExisted(currentScreenHash):
        graph.addScreen(Screen(views, currentScreenHash, currentScreenTree,
                               clickable_views))
        time.sleep(1)
        run_xbot_check(activity, output_dir, d)
        time.sleep(1)
    print(graph)
    screen = graph.getScreenFromExisted(currentScreenHash)
    if len(screen.clickableViews) == 0:
        d.key_press('BACK')
    for clickable_view in screen.clickableViews:
        if clickable_view not in screen.clickedViews:
            screen.addToClickedView(clickable_view)
            d.tap_view(clickable_view)

            start_exploration(activity, d, graph, output_dir, screen.nodeHash,clickable_view, t_end)



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
    gg_issue_path = output_directory + '/issues/'
    deeplinks_json = os.path.join(current_directory, app_name, 'deeplinks_params.json')
    log = current_directory + '/visited_rates/' + app_name + ".txt"
    check_and_create_dir(ss_path)
    check_and_create_dir(gg_issue_path)
    check_and_create_dir(current_directory + '/visited_rates/')
    unit_dynamic_testing(emulator, apk_path, atg_json, output_directory, deeplinks_json, atg_save_dir, login_options,
                         log,
                         reinstall=False)


if __name__ == '__main__':
    print(os.getcwd())
    outmost_directory = os.getcwd().replace('/apkExplore', '')
    login_options = {
        'hasLogin': True,
        'facebookLogin': False,
        'username': 'vuminhduc30@gmail.com',
        'password': 'minhduc123',
        'packageName': 'com.alibaba.aliexpresshd',
        'activityName': 'com.aliexpress.sky.user.ui.SkyShellActivity'
    }
    # run_deer(apk_file, emulator, outmost_directory)
    apks = [f for f in os.listdir("../input") if isfile(join(outmost_directory + "/input", f))]
    excluded_apps = ["Telegram.apk", "AliExpress.apk", "Wildberries.apk", "VidMate.apk"]
    # for apk in apks:
    #     if apk not in excluded_apps:
    #         dynamic_GUI_testing("emulator-5554", apk[:-4], outmost_directory, False, "phone-vertical",
    #                            "normal")
    dynamic_GUI_testing("emulator-5554", "AliExpress", os.getcwd().replace("/apkExplore", ""), login_options,
                        "phone-vertical", "normal")
    #
    #
    # unit_dynamic_testing("08221FDD4004DF", "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/input/alltrails.apk",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/activity_atg/alltrails.json",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/output/alltrails/08221FDD4004DF/setting1/activity_screenshots/",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/deeplinks_params.json",
    #                      '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/',
    #                      login_options, '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/visited_rates/alltrails.txt',)
