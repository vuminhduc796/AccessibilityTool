import os
import random
import json
import config.config as sys_config
import adbutils
import typer
import uiautomator2 as u2
import requests
import uiautomator2.exceptions

from guidedExplore.util import *

from guidedExplore.util import getActivityPackage, saveScreenshot
from guidedExplore.testing_path_planner import PathPlanner
from guidedExplore.hierachySolver import click_points_Solver, bounds2int
from guidedExplore.grantPermissonDetector import dialogSolver
import subprocess
from datetime import datetime
from uiautomator2 import Direction
from guidedExplore.activity_launcher import launch_activity_by_deeplinks, launch_activity_by_deeplink

dynamic_atg = {}


def random_bfs_explore(d, deviceId, path_planner, visited_activities, ss_path, timeout=60, swipe=False):
    d_activity, d_package, isLauncher = getActivityPackage(d)
    start_time = datetime.now()
    random_status = False

    # judge if the screen can swipe
    swipe = False
    xml = d.dump_hierarchy(compressed=True)

    leaves = click_points_Solver(xml)
    d.swipe_ext(Direction.FORWARD)
    xml2 = d.dump_hierarchy(compressed=True)
    leaves2 = click_points_Solver(xml2)
    leaves.sort()
    leaves2.sort()
    new_leaves_not_in_leaves = [i for i in leaves2 if i not in leaves]
    if len(new_leaves_not_in_leaves) > 2:
        swipe = True
        d.swipe_ext(Direction.BACKWARD)

    clicked_bounds = []
    cur_timeout = timeout
    while True:
        cur_time = datetime.now()
        delta = (cur_time - start_time).seconds
        if delta > cur_timeout:
            return

        _, _, cur_isLauncher = getActivityPackage(d)
        if cur_isLauncher != d_activity:
            full_cur_activity = path_planner.get_activity_full_path(d_activity)
            # d.app_start(d_package, full_cur_activity)
            deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                        full_cur_activity)
            status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
            if status:
                # get the screenshot
                if full_cur_activity not in visited_activities:
                    visited_activities.append(full_cur_activity)
                    screenshot = saveScreenshot(d, ss_path, full_cur_activity)
                    if screenshot is None:
                        print('Failed to save screenshot of  {}'.format(full_cur_activity))

        # random testing, click clickable pixel on the screen randomly
        if random_status:
            d_activity, d_package, isLauncher = getActivityPackage(d)
            path_planner.set_visited(d_activity)

            direction_list = [0, 1, 2, 2, 2]
            dire = random.choice(direction_list)
            if dire == 0:
                d.swipe_ext(Direction.FORWARD)
            elif dire == 1:
                d.swipe_ext(Direction.BACKWARD)

            xml = d.dump_hierarchy(compressed=True)
            leaves = click_points_Solver(xml)
            if len(leaves) == 0:
                d.press('back')
                continue

            cur_timeout = len(leaves) * 6
            cur_timeout = max(50, cur_timeout)
            cur_timeout = min(cur_timeout, 200)
            print('cur_timeout ' + str(cur_timeout))
            # not_click_leaves = [i for i in leaves if i not in clicked_bounds]
            # if len(not_click_leaves) == 0:
            #     d.press('back')
            #     continue
            action_point = random.choice(leaves)
            d.click((action_point[0] + action_point[2]) / 2, (action_point[1] + action_point[3]) / 2)
            # clicked_bounds.append(action_point)
            try:
                xml2 = d.dump_hierarchy(compressed=True)
            except uiautomator2.exceptions.JSONRPCError as e:
                print('java.lang.OutOfMemoryError')
                d.press('back')
                continue
            except requests.exceptions.ConnectTimeout as e2:
                print('HTTPConnectionPool')
                continue

            new_leaves = click_points_Solver(xml2)
            leaves.sort()
            new_leaves.sort()
            new_leaves_not_in_leaves = [i for i in new_leaves if i not in leaves]
            d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
            # get the screenshot
            if d2_activity not in visited_activities:
                visited_activities.append(d2_activity)
                screenshot = saveScreenshot(d, ss_path, d2_activity)
                if screenshot is None:
                    print('Failed to save screenshot of  {}'.format(d2_activity))

            if d2_activity != d_activity:
                if d_activity not in dynamic_atg.keys():
                    dynamic_atg[d_activity] = [d2_activity]
                elif d2_activity not in dynamic_atg[d_activity]:
                    dynamic_atg[d_activity].append(d2_activity)

            if len(new_leaves_not_in_leaves) >= 3 and d2_activity == d_activity:
                action_point = random.choice(new_leaves_not_in_leaves)
                d.click((action_point[0] + action_point[2]) / 2, (action_point[1] + action_point[3]) / 2)
                # new state, update the clicked bounds


        # first click all clickable widgets on the screen
        else:
            path_planner.set_visited(d_activity)
            testing_candidate_bounds_list = []
            # find clickable leaves
            xml = d.dump_hierarchy(compressed=True)
            leaves = click_points_Solver(xml)
            for leaf in leaves:
                if leaf in clicked_bounds:
                    continue
                d.click((leaf[0] + leaf[2]) / 2, (leaf[1] + leaf[3]) / 2)
                clicked_bounds.append(leaf)
                # d.sleep(0.5)

                d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
                if d2_activity != d_activity or isLauncher2:
                    # save atg
                    if d_activity not in dynamic_atg.keys():
                        dynamic_atg[d_activity] = [d2_activity]
                    elif d2_activity not in dynamic_atg[d_activity]:
                        dynamic_atg[d_activity].append(d2_activity)
                    # get the screenshot
                    if d2_activity not in visited_activities:
                        visited_activities.append(d2_activity)
                        screenshot = saveScreenshot(d, ss_path, d2_activity)
                        if screenshot is None:
                            print('Failed to save screenshot of  {}'.format(d2_activity))
                    testing_candidate_bounds_list.append(leaf)
                    path_planner.set_visited(d2_activity)
                    # d.press('back')
                    full_cur_activity = path_planner.get_activity_full_path(d_activity)
                    # d.app_start(d_package, full_cur_activity)
                    deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                                full_cur_activity)
                    status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

            if swipe:
                d.swipe_ext(Direction.FORWARD)
                xml2 = d.dump_hierarchy(compressed=True)
                leaves2 = click_points_Solver(xml2)
                for leaf in leaves2:
                    d.click((leaf[0] + leaf[2]) / 2, (leaf[1] + leaf[3]) / 2)
                    clicked_bounds.append(leaf)
                    # d.sleep(0.5)

                    d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
                    if d2_activity != d_activity or isLauncher2:
                        # save atg
                        if d_activity not in dynamic_atg.keys():
                            dynamic_atg[d_activity] = [d2_activity]
                        elif d2_activity not in dynamic_atg[d_activity]:
                            dynamic_atg[d_activity].append(d2_activity)
                        # get the screenshot
                        if d2_activity not in visited_activities:
                            visited_activities.append(d2_activity)
                            screenshot = saveScreenshot(d, ss_path, d2_activity)
                            if screenshot is None:
                                print('Failed to save screenshot of  {}'.format(d2_activity))

                        testing_candidate_bounds_list.append(leaf)
                        path_planner.set_visited(d2_activity)
                        # d.press('back')
                        full_cur_activity = path_planner.get_activity_full_path(d_activity)
                        # d.app_start(d_package, full_cur_activity)
                        deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                                    full_cur_activity)
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

                d.swipe_ext(Direction.BACKWARD)

            # after clicking all clickable widgets, begin to randomly click and test
            random_status = True


def login_with_facebook(d, login_options):
    # d.app_start('com.alltrails.alltrails', '.ui.authentication.mediaauth.AuthActivity')
    try :

        d.app_start(login_options['packageName'], login_options['activityName'])
        time.sleep(3)

        xml = d.dump_hierarchy()

        # check facebookLogin
        elementId = search_elements_from_XMLElement(xml, 'facebook')
        if elementId is None:
            return False
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()
            time.sleep(3)

        #     try to input username and password
        xml = d.dump_hierarchy()

        #
        passwordTextEditId = search_input_from_XMLElement(xml, 'password')
        if passwordTextEditId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=passwordTextEditId).set_text(login_options['password'])

            usernameTextEditId = search_input_from_XMLElement(xml, 'email')
            if usernameTextEditId is None:
                usernameTextEditId = search_input_from_XMLElement(xml, 'username')
            if usernameTextEditId is not None:
                d.implicitly_wait(20.0)
                d(resourceId=usernameTextEditId).set_text(login_options['username'])
                d.press("back")
                xml = d.dump_hierarchy()
                elementId = search_elements_from_XMLElement(xml, 'log in')
                if elementId is not None:
                    d.implicitly_wait(20.0)
                    d(resourceId=elementId).click()
                    time.sleep(3)

        # click continue button
        xml = d.dump_hierarchy()
        elementId = search_elements_from_XMLElement(xml, 'continue')
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()


    except Exception as e:

        print('Failed to start {} because {}'.format(login_options['activityName'], e))
        return False

    return True


def try_login(d, login_options):
    # d.app_start('com.alltrails.alltrails', '.ui.authentication.mediaauth.AuthActivity')
    try:
        d.app_start(login_options['packageName'], login_options['activityName'])
        time.sleep(3)
        xml = d.dump_hierarchy()

        # check if need an extra move
        elementId = search_elements_from_XMLElement(xml, 'already have an account')
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, 'log in')
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, 'sign in')
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()

        #     try to input username and password
        xml = d.dump_hierarchy()
        usernameTextEditId = search_input_from_XMLElement(xml, 'email')
        if usernameTextEditId is None:
            usernameTextEditId = search_input_from_XMLElement(xml, 'username')
        if usernameTextEditId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=usernameTextEditId).set_text(login_options['username'])

        passwordTextEditId = search_input_from_XMLElement(xml, 'password')
        if passwordTextEditId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=passwordTextEditId).set_text(login_options['password'])

        # click login button
        d.press("back")
        xml = d.dump_hierarchy()
        elementId = search_elements_from_XMLElement(xml, 'log in')
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, 'sign in')
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()


    except Exception as e:

        print('Failed to start {} because {}'.format(login_options['activityName'], e))
        return False

    return True


def unit_dynamic_testing(deviceId, apk_path, atg_json, ss_path, deeplinks_json, atg_save_dir, login_options,
                         log_save_path, test_time=1200, reinstall=False):
    visited_rate = []
    visited_activities = []
    installed1, packageName, mainActivity = installApk(apk_path, device=deviceId, reinstall=reinstall)
    if installed1 != 0:
        print('install ' + apk_path + ' fail.')
        return
    try:
        # check_arch = "adb -s " + deviceId + " shell getprop ro.product.cpu.abi"
        # res = subprocess.getoutput(check_arch)

        if sys_config.config_content['arm64'] == "true" or sys_config.config_content['arm64']:
            print("check connnection for M1")
            connect_arm64(deviceId)
        d = u2.connect(deviceId)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return

    test_start_time = datetime.now()

    # open launcher activity
    d.app_start(packageName)
    d.sleep(3)
    dialogSolver(d)

    if login_options['hasLogin']:
        try_login(d, login_options)
        d.sleep(3)

    if login_options['facebookLogin']:
        login_with_facebook(d, login_options)
        d.sleep(3)

    # get the screenshot of the first activity
    main_screenshot = saveScreenshot(d, ss_path, mainActivity)
    visited_activities.append(mainActivity)
    if main_screenshot is None:
        print('Failed to save screenshot of  {}'.format(mainActivity))

    # d.swipe_ext(Direction.FORWARD)
    # d.swipe_ext(Direction.BACKWARD)
    path_planner = PathPlanner(packageName, atg_json, deeplinks_json)
    delta = 0
    while delta <= test_time:
        random_bfs_explore(d, deviceId, path_planner, visited_activities, ss_path, timeout=60, swipe=True)
        print('---------------------- visited rate: ', path_planner.get_visited_rate())
        visited_rate.append(path_planner.get_visited_rate())

        while True:
            next_activity = path_planner.pop_next_activity()
            if next_activity is not None:
                # d.app_start(d_package, next_activity)
                deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(packageName,
                                                                                            next_activity)
                status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                if status:
                    path_planner.set_visited(next_activity)

                    # save the screenshot of the current activity
                    if next_activity not in visited_activities:
                        screenshot = saveScreenshot(d, ss_path, next_activity)
                        visited_activities.append(next_activity)
                        if screenshot is None:
                            print('Failed to save screenshot of  {}'.format(next_activity))
                    break
            else:
                print('no next activity in ATG')
                unvisited = path_planner.get_unvisited_activity_deeplinks()
                if unvisited is None:
                    print('no activity, finish')
                    print('visited rate:%s' % (path_planner.get_visited_rate()))
                    visited_rate.append(path_planner.get_visited_rate())
                    path_planner.log_visited_rate(visited_rate, path=log_save_path)
                    cur_test_time = datetime.now()
                    delta = (cur_test_time - test_start_time).total_seconds()
                    print('time cost:' + str(delta))
                    return
                else:
                    for i in unvisited:
                        activity, deeplinks, actions, params = i
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                        path_planner.set_popped(activity)
                        if status:
                            path_planner.set_visited(activity)
                            if activity not in visited_activities:
                                screenshot = saveScreenshot(d, ss_path, activity)
                                visited_activities.append(activity)
                                if screenshot is None:
                                    print('Failed to save screenshot of  {}'.format(activity))

                            random_bfs_explore(d, deviceId, path_planner, visited_activities, ss_path, timeout=60,
                                               swipe=True)
                            break

        cur_test_time = datetime.now()
        delta = (cur_test_time - test_start_time).total_seconds()

    with open(atg_save_dir, 'w') as f:
        json.dump(dynamic_atg, f)

    print('visited rate:%s in %s seconds' % (path_planner.get_visited_rate(), test_time))
    path_planner.log_visited_rate(visited_rate, path=log_save_path)
    return


def check_and_create_dir(dir_name):
    if not os.path.exists(dir_name):
        # in case multiple directories need to be created. for example /activity_screenshots/appRelease
        os.makedirs(dir_name)


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


def connect_arm64(deviceId):
    atx_agent_filename = 'atx-agent_0.10.0_linux_arm64.tar.gz'
    atx_agent_url = 'https://github.com/openatx/atx-agent/releases/download/0.10.0/' + atx_agent_filename
    temp_dir = '../../../tmp_atx-agent/arm64/'
    # download atx_agent
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(temp_dir + "atx-agent"):
        typer.secho("Start downloading atx-agent...", fg=typer.colors.MAGENTA)
        command = 'curl -LJ ' + atx_agent_url + ' > ' + temp_dir + atx_agent_filename
        typer.secho(subprocess.getoutput(command), fg=typer.colors.MAGENTA)
        # unzip tar.gz
        command = 'tar zxvf ' + temp_dir + atx_agent_filename + ' -C ' + temp_dir
        typer.secho(subprocess.getoutput(command), fg=typer.colors.MAGENTA)
    else:
        typer.secho("Use cache", fg=typer.colors.MAGENTA)
    # chmod
    chmod_command = 'adb -s ' + deviceId + ' shell chmod 755 /data/local/tmp/*'
    typer.secho(subprocess.getoutput(chmod_command), fg=typer.colors.MAGENTA)
    # push atx_agent to the device
    push_command = 'adb -s ' + deviceId + ' push ' + temp_dir + 'atx-agent /data/local/tmp/atx_arm'
    typer.secho(subprocess.getoutput(push_command), fg=typer.colors.MAGENTA)
    # execute atx_agent
    launch_command = 'adb -s ' + deviceId + ' shell /data/local/tmp/atx_arm server --nouia -d --addr ' \
                                            '127.0.0.1:7912'
    typer.secho(subprocess.getoutput(launch_command), fg=typer.colors.MAGENTA)
