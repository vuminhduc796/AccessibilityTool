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
    try :

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

    # try automatic login
    if login_options['hasLogin']:
        email_password_login(d, login_options)

    if login_options['facebookLogin']:
        login_with_facebook(d, login_options)

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
    login_options = {
        'hasLogin': True,
        'facebookLogin': False,
        'username': 'test',
        'password': 'test',
        'packageName': 'com.alltrails.alltrails',
        'activityName': 'com.alltrails.alltrails.ui.authentication.AuthenticationActivity'
    }
    unit_dynamic_testing("08221FDD4004DF", "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/input/alltrails.apk",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/activity_atg/alltrails.json",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/output/alltrails/08221FDD4004DF/setting1/activity_screenshots/",
                         "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/deeplinks_params.json",
                         '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/',
                         login_options, '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/visited_rates/alltrails.txt',)