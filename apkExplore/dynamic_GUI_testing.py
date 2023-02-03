import hashlib
import random
import json
from os.path import isfile, join

import os
import subprocess
from datetime import datetime
from apkExplore.droidbot.exploration.Graph import Graph, Screen, Edge
from apkExplore.droidbot.intent import Intent
from apkExplore.xbot_kit import scan_and_return, collect_results, clean_up_scanner_data
from apkExplore.droidbot.device import Device
from apkExplore.droidbot.app import App
import time

from owleyes.cnn_cam3 import owleyes_scan


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


def run_xbot_check(activity, output_dir, device, numberedActName):
    device.adb.shell(
        "settings put secure enabled_accessibility_services com.google.android.apps.accessibility.auditor/com.google.android.apps.accessibility.auditor.ScannerService")
    scanner_pkg = 'com.google.android.apps.accessibility.auditor'
    adb_command = "adb -s " + device.serial

    clean_up_scanner_data(adb_command, scanner_pkg)
    print('Accessibility Scanner: Starting scan...')
    scan_and_return(device.serial, activity, output_dir, device, numberedActName)
    print('Accessibility Scanner: Scan complete. Clean up...')
    clean_up_scanner_data(adb_command, scanner_pkg)
    device.adb.shell("am force-stop com.google.android.apps.accessibility.auditor")


def match_crash_log(output_dir):
    crashRecords = {}
    with open(output_dir + '/crashlog.txt', 'r') as f:
        crashlog = f.read()
        for line in crashlog.splitlines():
            if "FATAL EXCEPTION" in line:
                crashtimeStr = line.split("  ")[0]
                crashtime = datetime.strptime(crashtimeStr, "%m-%d %H:%M:%S.%f")
                crashRecords[crashtimeStr] = {
                    "crash_time": crashtime,
                    "crash_log": line + '\n',
                    "action_detail": {
                        "activity": "",
                        "clicked_view": "",
                    },
                }
            else:
                crashtimeStr = line.split("  ")[0]
                if crashtimeStr in crashRecords:
                    crashRecords[crashtimeStr]["crash_log"] += line + '\n'

    with open(output_dir + '/clicked_views.txt', 'r') as f:
        clicked_views = f.read()
        for line in clicked_views.splitlines():
            if ';;;' not in line:
                continue
            clickTime = line.split(" ;;; ")[0]
            # change the time format to datatime format
            clickTime = datetime.strptime(clickTime, "%m-%d %H:%M:%S.%f")
            # check if the time is same as the crash time or within 1 second
            for crashRecordTime in crashRecords:
                if time == crashRecordTime or (
                        int(clickTime.timestamp()) - int(crashRecords[crashRecordTime]['crash_time'].timestamp()) <= 2):
                    crashRecords[crashRecordTime]["action_detail"]["clicked_view"] = line.split(" ;;; ")[1]
                    crashRecords[crashRecordTime]["action_detail"]["activity"] = line.split(" ;;; ")[2]

    # serialize the timestamp in crashRecords
    for crashRecordTime in crashRecords:
        crashRecords[crashRecordTime]["crash_time"] = crashRecords[crashRecordTime]["crash_time"].strftime(
            "%m-%d %H:%M:%S.%f")
    # save the crash records to a file
    with open(output_dir + '/crash_records.json', 'w') as f:
        json.dump(crashRecords, f)

    # remove the crashlog and clicked_views file
    # os.remove(output_dir + '/crashlog.txt')
    # os.remove(output_dir + '/clicked_views.txt')

    return crashRecords


def unit_dynamic_testing(deviceId, apk_path, atg_json, output_dir, deeplinks_json, atg_save_dir, current_graph,
                         login_options,
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

    if not isAppOpened:
        print("Exploration: APK failed to install")
        return
    mainActivity = targetApp.main_activity

    numberOfActivities = 0
    numberOfSuccessful = 0
    # open app and get the screenshot of the first activity
    if isAppOpened:
        # start to track the crash
        crashRecords = {}
        with open(output_dir + '/crash_records.json', 'w') as f:
            json.dump(crashRecords, f)
        # with open(output_dir + '/crashlog.txt', 'w') as f:
        #     proc = subprocess.Popen(['adb', 'logcat', '--buffer=crash'], stdout=f)

        # d.start_app(targetApp)
        # time.sleep(2)

        with open(deeplinks_json, 'r', encoding='utf8') as f:
            activities = []
            try:
                activities = json.loads(f.read())
            except:
                print("No acitivity found")
            print(activities)
            if len(activities) == 0:
                d.install_app(targetApp)
                t_end = time.time() + 1200
                history = {
                    "activity": d.get_top_activity_name(),
                    "action": "root",
                }
                start_exploration(d.get_top_activity_name(), d, current_graph, output_dir, "", "", t_end, targetApp, 0, history)

            print("Exploration: total number of activities found: " + str(len(activities)))
            for activity in activities:
                numberOfActivities += 1
                explore_activity(activities, activity, current_graph, d, numberOfActivities, numberOfSuccessful,
                                 output_dir, targetApp)

    # try automatic login

    visited_activities.append(mainActivity)

    d.disconnect()

    # stop the crash log
    # proc.terminate()
    # proc.wait()

    # read the crash log and clicked_views and match them with the timestamp
    # match_crash_log(output_dir)


def explore_activity(activities, activity, current_graph, d, numberOfActivities, numberOfSuccessful, output_dir,
                     targetApp):
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
        time.sleep(2)

        # if login_options['hasLogin']:
        #     print("login")
        #     email_password_login(d, login_options)
        #
        # if login_options['facebookLogin']:
        #     login_with_facebook(d, login_options)

        currentScreen = d.get_top_activity_name().split("/")[-1]
        if True:
            print('Exploration: currentScreen {} in activity {}'.format(currentScreen, activity))
            t_end = time.time() + 300
            history = {
                "activity": currentScreen,
                "action": "root",
            }
            start_exploration(activity, d, current_graph, output_dir, "", "", t_end, targetApp, 0, history)
            numberOfSuccessful += 1
            time.sleep(2)
            # d.go_home()
            break
        else:
            print('Exploration: currentScreen {} not in activity {}'.format(currentScreen, activity))
        d.go_home()
        time.sleep(1)
        d.start_app(targetApp)
        time.sleep(1)
    print(
        "Exploration: total: " + numberOfActivities.__str__() + ", success: " + numberOfSuccessful.__str__())


MAX_DEPTH = 5


def start_exploration(activity, d, graph, output_dir, previous_view_hash, clicked_btn, t_end, targetApp, depth,
                      history):
    with open(output_dir + '/crashlogTemp.txt', 'w') as f:

        proc = subprocess.Popen(['adb', '-s', d.serial, 'logcat', '--buffer=crash'], stdout=f)
    # early exit when time is up or depth is exceeded
    depth += 1
    if time.time() > t_end:
        print("Exploration: time is up")
        return False

    time.sleep(1)

    temp_views = d.get_views()
    if temp_views is None:
        d.key_press('BACK')
        time.sleep(2)
        temp_views = d.get_views()
    currentActivity = d.get_top_activity_name().split("/")[-1]
    while currentActivity[0] == '.':
        currentActivity = currentActivity[1:]
    if currentActivity in "com.android.launcher3/.Launcher":
        print("Exploration: App exited -- restart")
        d.start_app(targetApp)

    currentScreenHash, views, clickable_views, scrollable_views = hash_screen(currentActivity, temp_views)

    # TODO: support text input views and other actions such as swipe and scroll

    if not graph.checkScreenExisted(currentScreenHash):
        newAct = graph.getActivityStoringName(currentActivity)
        graph.addScreen(Screen(views, currentScreenHash, newAct,
                               clickable_views))
        collect_current_state(d, currentActivity, newAct, output_dir)

        d.pause_tool()
        time.sleep(1)
        run_xbot_check(currentActivity, output_dir, d, newAct)
        time.sleep(2)
        owleyes_scan(currentActivity, newAct, output_dir)
        d.resume_tool()
        # wait for screen is fully loaded
        time.sleep(2)
        # check if app exited
        if d.get_top_activity_name() == "com.android.launcher3/.Launcher":
            print("Exploration: App exited -- restart")
            d.start_app(targetApp)
    else:
        print("Exploration: Screen existed")

    print(graph)
    screen = graph.getScreenFromExisted(currentScreenHash)
    numberedActivityName = screen.nodeActivityName

    # add Edge
    if previous_view_hash != currentScreenHash:

        previousNode = graph.getScreenFromExisted(previous_view_hash)
        if previousNode is None:
            previousNumberedActName = ""
        else:
            previousNumberedActName = graph.getScreenFromExisted(previous_view_hash).nodeActivityName

        newEdge = Edge(clicked_btn, previousNumberedActName, numberedActivityName)
        graph.addEdge(newEdge)

    # navigation
    time.sleep(1)

    if depth >= MAX_DEPTH - 1:
        print("Exploration: Deep reached")
        return False

    # back when no view to click
    if len(screen.clickableViews) == 0 or len(screen.clickableViews) == len(screen.clickedViews):
        # check this
        for view in scrollable_views:
            d.view_scroll_diagonal(view)
            time.sleep(2)
            temp_views = d.get_views()
            currentActivity = d.get_top_activity_name().split("/")[-1]
            newHash, newViews, clickable_views, scrollable_views = hash_screen(currentActivity, temp_views)
            if newHash != currentScreenHash:
                newHistory = {
                    "activity": currentActivity,
                    "action": {
                        "action": "Scroll",
                        "view": str(view),
                    },
                    "parent": history,
                }
                start_exploration(activity, d, graph, output_dir, screen.nodeHash, "Scroll", t_end, targetApp,
                                  depth, newHistory)

        d.key_press('BACK')
        time.sleep(1)
        temp_views = d.get_views()
        currentActivity = d.get_top_activity_name().split("/")[-1]
        newHash, newViews, clickable_views, scrollable_views = hash_screen(currentActivity, temp_views)

        # solve soft keyboard prevent back issues
        if newHash == currentScreenHash:
            d.key_press('BACK')
            time.sleep(1)
        return True

    # click each element on the screen (DFS)
    isContinue = True
    while isContinue is True:
        unclicked_views = []
        for element in screen.clickableViews:
            if element not in screen.clickedViews:
                unclicked_views.append(element)
        if len(unclicked_views) > 0:
            click_view = unclicked_views[random.randint(0, len(unclicked_views) - 1)]
        elif len(unclicked_views) <= 0:
            isContinue = False
            break
        print("Exploration: Clicking " + str(len(unclicked_views)) + " in " + str(len(screen.clickedViews)) + "/" + str(
            len(screen.clickableViews)))

        screen.addToClickedView(click_view)
        time.sleep(1)
        d.tap_view(click_view)
        # save the clicked view and the current screen by timestamp
        with open(output_dir + "/clicked_views.txt", "a+") as myfile:
            # save time to time format mm-dd H:M:S
            myfile.write(str(datetime.now().strftime("%m-%d %H:%M:%S.%f")) + " ;;; " + str(
                click_view) + " ;;; " + currentActivity + '\n\n')
        time.sleep(1)

        # check if crash by checking the crash file have content
        with open(output_dir + '/crashlogTemp.txt', 'r') as f:
            crashlog = f.read()
            for line in crashlog.splitlines():
                # if package name is in line
                if targetApp.package_name in line:
                    print("Exploration: App crashed")
                    # save the temp log to crashlog with time and action trace
                    crashtimeStr = line.split("  ")[0]
                    crashtime = datetime.strptime(crashtimeStr, "%m-%d %H:%M:%S.%f")
                    # read crashRecords
                    with open(output_dir + '/crash_records.json', 'r') as f:
                        crashRecords = json.load(f)
                    crashRecords[crashtimeStr] = {
                        "crash_time": str(crashtime),
                        "crash_log": crashlog,
                        "action_trace": history,
                    }
                    # write crashRecords
                    with open(output_dir + '/crash_records.json', 'w') as f:
                        json.dump(crashRecords, f)

        # clear the temp file
        with open(output_dir + '/crashlogTemp.txt', 'w') as f:
            f.write('')
        # restart the proc
        proc.terminate()
        proc.wait()
        newHistory = {
            "activity": currentActivity,
            "action": {
                "type": "click",
                "view": str(click_view),
            },
            "parent": history,
        }
        isContinue = start_exploration(activity, d, graph, output_dir, screen.nodeHash, click_view, t_end, targetApp,
                                       depth, newHistory)

    return True


def collect_current_state(d, activity, numberedActName, output_dir):
    dir_path = os.path.join(output_dir, "states", activity)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = numberedActName + ".json"
    filepath = os.path.join(dir_path, filename)
    try:
        stateJson = d.get_current_state().to_dict()
        with open(filepath, 'w') as f:
            json.dump(stateJson, f, indent=4, separators=(',', ': '))
    except Exception as e:
        return


def hash_screen(currentActivity, temp_views):
    if temp_views is None:
        return "Not found", [], [], []
    views = []
    for view in temp_views:
        view_bound = view["bounds"]
        top_bound = view_bound[0][1]
        left_bound = view_bound[0][0]
        bottom_bound = view_bound[1][1]
        right_bound = view_bound[1][0]

        if bottom_bound > top_bound and right_bound > left_bound:
            views.append(view)
    currentScreenHash = ""

    clickable_views = []
    scrollable_views = []
    for view in views:
        if view["clickable"] is True and view['enabled'] is True:
            clickable_views.append(view)
        if view['scrollable'] is True:
            scrollable_views.append(view)

    for view in clickable_views:
        viewHash = str(view["editable"]) + str(view[
                                                   "clickable"]) + view["class"] + view["size"] + str(view[
                                                                                                          "selected"]) + currentActivity

        if viewHash not in currentScreenHash:
            currentScreenHash += viewHash
    currentScreenHash = hashlib.sha1(currentScreenHash.encode("utf-8")).hexdigest()
    return currentScreenHash, views, clickable_views, scrollable_views


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

    current_graph = Graph(app_name, android_device, current_setting)
    print("Exploration: Start Exploration")
    unit_dynamic_testing(emulator, apk_path, atg_json, output_directory, deeplinks_json, atg_save_dir, current_graph,
                         login_options,
                         log,
                         reinstall=False)


if __name__ == '__main__':
    outmost_directory = os.getcwd().replace('/apkExplore', '')
    # login_options = {
    #     'hasLogin': True,
    #     'facebookLogin': False,
    #     'username': 'vuminhduc30@gmail.com',
    #     'packageName': 'com.alibaba.aliexpresshd',
    #     'activityName': 'com.aliexpress.sky.user.ui.SkyShellActivity'
    # }
    # run_deer(apk_file, emulator, outmost_directory)

    apks = [f for f in os.listdir("../input") if isfile(join(outmost_directory + "/input", f))]
    excluded_apps = ["Telegram.apk", "AliExpress.apk", "Wildberries.apk", "VidMate.apk"]
    # for apk in apks:
    #     if apk not in excluded_apps:
    #         dynamic_GUI_testing("emulator-5554", apk[:-4], outmost_directory, False, "phone-vertical",
    #                            "normal")

    graph = Graph("AliExpress", "phone-vertical", "normal")
    dynamic_GUI_testing("emulator-5554", "note", os.getcwd().replace("/apkExplore", ""), {},
                        "phone-vertical", "normal")

    # attempt to get resource -> get xml
    # app = App(os.getcwd().replace("/apkExplore", "") + "/input/AliExpress.apk")
    # print(app.apk.get_android_resources().resource_values)
    #
    #
    # unit_dynamic_testing("08221FDD4004DF", "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/input/alltrails.apk",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/activity_atg/alltrails.json",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/output/alltrails/08221FDD4004DF/setting1/activity_screenshots/",
    #                      "/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/deeplinks_params.json",
    #                      '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/alltrails/',
    #                      login_options, '/Users/han/GoogleDrive/Monash/project/AccessibilityTool/guidedExplore/data/visited_rates/alltrails.txt',)
