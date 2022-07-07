'''
Authors: Sen Chen and Lingling Fan
'''

import os, shutil
import re
import subprocess
import time, csv

adb = 'adb'
# adb = "adb -s %s"%(run_rpk_explore_apk.emulator)
# folder_name = run.folder_name
# tmp_dir = run_rpk_explore_apk.tmp_file

# adb = ''
tmp_dir = ''
act_paras_file = ''
defined_pkg_name = ''
current_font_size = "normal"
current_dark_mode = "light_mode"
used_pkg_name = ''
pressLocations = {
    "emulator-5554": {
        "name": "phone-vertical",
        "check": {
            "x": 200,
            "y": 200
        },
        "share": {
            "x": 1221,
            "y": 279
        },

    },
    "emulator-5558": {
        "name": "phone-horizontal",
        "check": {
            "x": 200,
            "y": 200
        },
        "share": {
            "x": 2817,
            "y": 233
        },
    },
    "emulator-5556": {
        "name": "tablet-horizontal",
        "check": {
            "x": 200,
            "y": 200
        },
        "share": {
            "x": 2376,
            "y": 88
        },
    },
    "emulator-5560": {
        "name": "tablet-vertical",
        "check": {
            "x": 200,
            "y": 200
        },
        "share": {
            "x": 1680,
            "y": 112
        },
    },
}


def installAPP(new_apkpath, apk_name, results_folder):
    appPath = new_apkpath
    get_pkgname(appPath)

    cmd = adb + " install -r " + appPath

    out = subprocess.getoutput(cmd)
    for o in out.split('\n'):
        if 'Failure' in o or 'Error' in o:
            print('install failure: %s' % apk_name)
            print(out)
            csv.writer(open(os.path.join(results_folder, 'installError.csv'), 'a')).writerow(
                (apk_name, out.replace('\n', ', ')))
            return 'Failure'
    print('Install Success')

    return 'Success'


def uninstallApp(package):
    cmd = adb + " uninstall " + package
    os.system(cmd)


# def take_screenshot(act, appname):
#     path = os.getcwd()
#     os.system(adb + ' shell screencap -p /sdcard/%s.png'%act)
#     d_path = os.path.join(get_repackaged.screenshot_folder, appname)
#     if not os.path.exists(d_path):
#         os.makedirs(d_path)
#     os.chdir(d_path)
#     os.system(adb + ' pull /sdcard/%s.png'%act)
#     os.system(adb + ' shell rm /sdcard/%s.png'%act)
#     os.chdir(path)

def get_screen_size():
    cmd = adb + " shell wm size"
    print(cmd)
    process = os.popen(cmd)
    output = process.read()
    m = re.search(r'(\d+)x(\d+)', output)
    if m:
        # (w,h)
        return int(m.group(1))
    return None


def scan_and_return():
    time.sleep(1)

    # scan and share
    # os.system(adb + ' shell input tap 110 170')
    # 945,1650

    # os.system(adb + ' shell input tap 720 826')
    time.sleep(1)
    current_emulator = adb[-13:]
    print(pressLocations.get(current_emulator))

    os.system(adb + ' shell input tap ' + str(pressLocations.get(current_emulator).get("check").get("x")) + " " + str(
        pressLocations.get(current_emulator).get("check").get("y")))
    time.sleep(2)

    screensize = get_screen_size()
    #horizontal phone need higher cut in cuz more pixel
    if current_emulator == "emulator-5558":
        print("shhudd")
        os.system(adb + ' shell input tap ' + str(int(screensize) - 360) + " " + str(170))
    else:
        os.system(adb + ' shell input tap ' + str(int(screensize) - 170) + " " + str(170))
    time.sleep(3)
    # cancel and back
    os.system(adb + ' shell input keyevent 4')
    time.sleep(1)
    os.system(adb + ' shell input keyevent 3')
    time.sleep(1)


def clean_tmp_folder(folder):
    for f in os.listdir(folder):
        file = os.path.join(folder, f)
        # For macbook
        # os.system("chmod +x " + file)
        if os.path.isdir(file):
            shutil.rmtree(file)
        # os.remove(file)


def unzip(zipfile, activity):
    '''unzip result file and delete zip file'''
    cmd = 'unzip -o "%s" -d "%s"' % (zipfile, zipfile.split('.zip')[0])
    os.system(cmd)

    os.system('rm %s' % zipfile)
    # rename txt and png file name
    issue_folder = zipfile.split('.zip')[0]
    if os.path.exists(issue_folder) and os.path.isdir(issue_folder):

        for f in os.listdir(issue_folder):
            folder = os.path.join(issue_folder)
            if not os.path.exists(folder):
                os.makedirs(folder)
            if f.endswith('.png'):
                mv_cmd = 'mv "%s" "%s/%s.png"' % (os.path.join(issue_folder, f), folder, activity)
                os.system(mv_cmd)
            if f.endswith('.txt'):
                mv_cmd = 'mv "%s" "%s/%s.txt"' % (os.path.join(issue_folder, f), folder, activity)
                os.system(mv_cmd)


def collect_results(activity, appname, accessbility_folder, results_outputs):
    print("collectResultFunc")
    scanner_pkg = 'com.google.android.apps.accessibility.auditor'
    print('Collecting scan results from device...')

    # To save issues and screenshot temporarily in order to rename.
    tmp_folder = os.path.join(accessbility_folder, tmp_dir)
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    '''Pull issues and rename'''
    issue_path = os.path.join(results_outputs, 'issues')
    if not os.path.exists(issue_path):
        os.makedirs(issue_path)
    pull_results = adb + " pull /data/data/%s/cache/export/ %s" % (scanner_pkg, tmp_folder)
    # pull_results = adb + " pull /data/data/ %s" % ("./testhere")
    os.system(pull_results)

    zip_folder = os.path.join(tmp_folder + "/export")

    if os.path.exists(zip_folder):
        for zip in os.listdir(zip_folder):
            if zip.endswith('.zip'):
                os.system('mv "%s/%s" "%s/%s.zip"' % (zip_folder, zip, issue_path, activity))

    clean_tmp_folder(tmp_folder)

    if os.path.exists(os.path.join(issue_path, activity + '.zip')):
        unzip(os.path.join(issue_path, activity + '.zip'), activity)

    # '''Pull screenshot and rename'''
    # screenshot_path = os.path.join(results_outputs, appname, pressLocations.get(adb[-13:]).get("name"), 'screenshots')
    # if not os.path.exists(screenshot_path):
    #     os.makedirs(screenshot_path)
    # pull_screenshots = adb + " pull /data/data/%s/files/screenshots/ %s" % (scanner_pkg, tmp_folder)
    # os.system(pull_screenshots)
    # for png in os.listdir(tmp_folder):
    #     if not png.endswith('thumbnail.png'):
    #         os.system('mv "%s/%s" "%s/%s"'%(tmp_folder,png,screenshot_path,activity))
    clean_tmp_folder(tmp_folder)

    clean_results = adb + ' shell rm -rf /data/data/%s/cache/export/' % (scanner_pkg)
    os.system(clean_results)

    clean_screenshots = adb + ' shell rm -rf /data/data/%s/files/screenshots' % (scanner_pkg)
    os.system(clean_screenshots)


def check_current_screen():
    cmd = adb + " shell dumpsys activity activities | grep mResumedActivity"
    cmd1 = adb + " logcat -t 100 | grep Error"
    cmd2 = adb + " logcat -t 100 | grep Exception"
    # if pkg in commands.getoutput(cmd).split('\n')[0] and (not 'Exception' in commands.getoutput(cmd2)):
    if (not 'Error:' in subprocess.getoutput(cmd1)) and (not 'Exception:' in subprocess.getoutput(cmd2)) \
            and (not 'com.android.launcher3' in subprocess.getoutput(cmd)):
        return True
    return False


def check_current_screen_new(activity, appname, results_outputs):
    '''dump xml check whether it contains certain keywords:
        has stopped, isn't responding, keeps stopping, DENY, ALLOW
    '''
    print("checkCurrentFunc")
    keywords = ['has stopped', 'isn\'t responding', 'keeps stopping']

    '''dump xml and check'''
    print(adb)
    layout_path = os.path.join(results_outputs, 'layouts')
    if not os.path.exists(layout_path):
        os.makedirs(layout_path)
    print("====== dump =======")
    os.system(adb + ' shell uiautomator dump /sdcard/%s.xml' % activity)
    print("====== pull xml =======")
    pull_xml = adb + ' pull /sdcard/%s.xml %s' % (activity, layout_path)
    os.system(pull_xml)
    print("====== clean xml =======")
    clean_xml = adb + ' shell rm /sdcard/%s.xml' % activity
    os.system(clean_xml)

    # check whether it crashes
    layout_path = os.path.join(layout_path, activity + '.xml')
    for word in keywords:
        result = subprocess.getoutput('grep "%s" %s' % (word, layout_path))
        if not result == '':
            # if crash, remove xml from layout folder
            os.system('rm %s' % layout_path)
            return 'abnormal'
    # check whether it is a permission dialog
    if not subprocess.getoutput('grep -i "ALLOW" %s' % (layout_path)) == '' and not subprocess.getoutput(
            'grep -i "DENY" %s' % (layout_path)) == '':
        os.system(adb + ' shell input tap 780 1080')  # tap ALLOW
        print("hehe")
        time.sleep(1)
        cmd = adb + " shell dumpsys activity activities | grep mResumedActivity"
        cmdd = adb + " shell dumpsys activity activities | grep mFocusedActivity"
        if not 'com.android.launcher3' in subprocess.getoutput(
                cmd) and not 'com.android.launcher3' in subprocess.getoutput(cmdd):
            return 'normal'
        else:
            os.system('rm %s' % layout_path)
            return 'abnormal'

    cmd = adb + " shell dumpsys activity activities | grep mResumedActivity"
    cmdd = adb + " shell dumpsys activity activities | grep mFocusedActivity"
    if not 'com.android.launcher3' in subprocess.getoutput(cmd) and not 'com.android.launcher3' in subprocess.getoutput(
            cmdd):
        return 'normal'
    else:
        os.system('rm %s' % layout_path)
        return 'abnormal'


def explore(activity, appname, results_folder, results_outputs):
    print("exploreFunc")
    current = check_current_screen_new(activity, appname, results_outputs)
    print(current)
    if current == 'abnormal':
        # click home and click 'ok' if crashes (two kinds of 'ok's)
        os.system(adb + ' shell input tap 540 1855')
        time.sleep(1)

        # os.system(adb + ' shell input tap 899 1005')
        # os.system(adb + ' shell input tap 165 990')
        # time.sleep(1)
        # os.system(adb + ' shell input tap 163 1060')
        # os.system(adb + ' shell input tap 165 930')
        # time.sleep(1)
        return

    if current == 'normal':
        scan_and_return()
        collect_results(activity, appname, results_folder, results_outputs)


def clean_logcat():
    cmd_clean = adb + ' logcat -c'
    subprocess.getoutput(cmd_clean)


def init_d(activity, d):
    d[activity] = {}
    d[activity]['actions'] = ''
    d[activity]['category'] = ''

    return d


def extract_activity_action(path):
    # {activity1: {actions: action1, category: cate1}}
    # new format: {activity: [[action1, category1],[action2, category2]]}
    d = {}
    flag = 0
    for line in open(path, 'r').readlines():
        line = line.strip()

        if line.startswith("<activity"):
            print(line)
            activity = line.split('android:name="')[1].split('"')[0]
            print(activity)
            if activity.startswith('.'):
                activity = used_pkg_name + activity
            print(" activity: " + activity + " " + used_pkg_name)
            if not activity in d.keys() and used_pkg_name in activity:
                # d = init_d(activity, d) # some activities may have different actions and categories
                d[activity] = []
                flag = 1
            if line.endswith(
                    '/>'):  # if activity ends in one line, it has no actions, we only record its activity name.
                flag = 0
                continue

        elif line.startswith("<intent-filter") and flag == 1:
            flag = 2
            action_category_pair = ['', '']
        elif line.startswith('<action') and flag == 2:
            action = line.split('android:name="')[1].split('"')[0]
            action_category_pair[0] = action
        elif line.startswith('<category') and flag == 2:
            category = line.split('android:name="')[1].split('"')[0]
            action_category_pair[1] = category
        elif line.startswith('</intent-filter>') and flag == 2:
            flag = 1
            if not action_category_pair[0] == '' or not action_category_pair[1] == '':
                d[activity].append(action_category_pair)
        elif line.startswith('</activity>'):
            flag = 0
        else:
            continue

    return d


def get_full_activity(component):
    print("fullActFunc")
    '''get activity name, component may have two forms:
            1. com.google.abc/com.google.abc.mainactivity
            2. com.google.abc/.mainactivity
    '''
    act = component.split('/')[1]
    if act.startswith('.'):
        activity = component.split('/')[0] + act
    else:
        activity = act

    return activity


def convert(api, key, extras):
    print("convertFunc")
    if api == 'getString' or api == 'getStringArray':
        extras = extras + ' --es ' + key + ' test'
    if api == 'getInt' or api == 'getIntArray':
        extras = extras + ' --ei ' + key + ' 1'
    if api == 'getBoolean' or api == 'getBooleanArray':
        extras = extras + ' --ez ' + key + ' False'
    if api == 'getFloat' or api == 'getFloatArray':
        extras = extras + ' --ef ' + key + ' 0.1'
    if api == 'getLong' or api == 'getLongArray':
        extras = extras + ' --el ' + key + ' 1'
    return extras


def get_act_extra_paras(activity):
    print("get_act_extra_parasFunc")
    for line in open(act_paras_file, 'r').readlines():
        if line.strip() == '':
            continue
        if line.split(":")[0] == activity:
            if line.split(":")[1].strip() == '':
                return ''
            else:
                paras = line.split(':')[1].strip()
                extras = ''
                for each_para in paras.split(';'):
                    if '__' in each_para:
                        # api may refer to getString, getInt, ....
                        api = each_para.split('__')[0]
                        key = each_para.split('__')[1]
                        extras = convert(api, key, extras)
                return extras


def startAct(component, action, cate, appname, results_folder, results_outputs):
    print("startAct")
    clean_logcat()
    cmd = adb + ' shell am start -S -n %s' % component
    if not action == '':
        cmd = cmd + ' -a ' + action
    if not cate == '':
        cmd = cmd + ' -c ' + cate

    activity = get_full_activity(component)
    extras = get_act_extra_paras(activity)

    if extras != None:
        cmd = cmd + ' ' + extras
    os.system(cmd)
    time.sleep(3)

    return explore(activity, appname, results_folder, results_outputs)


# def save_activity_to_csv(accessbility_folder, app_name,  pkg, all_activity_num):
#     csv_file = os.path.join(accessbility_folder, 'log.csv')
#     csv.writer(open(csv_file,'ab')).writerow((app_name, pkg, all_activity_num))

# ('apk_name', 'pkg_name', 'all_act_num', 'launched_act_num','act_not_launched','act_num_with_issue')
def save_activity_to_csv(results_folder, apk_name, all_act_num, launched_act_num, act_not_launched, act_num_with_issue):
    csv_file = os.path.join(results_folder, 'log.csv')
    csv.writer(open(csv_file, 'a')).writerow(
        (apk_name, used_pkg_name, all_act_num, launched_act_num, act_not_launched, act_num_with_issue))


def parseManifest(new_apkpath, apk_name, results_folder, decompilePath, results_outputs):
    print("Parsing " + apk_name)

    if not os.path.exists(new_apkpath):
        print("cannot find the decomplied app: " + apk_name)
        return

    manifestPath = os.path.join(decompilePath, apk_name, "AndroidManifest.xml")

    if not os.path.exists(manifestPath):
        print("there is no AndroidManifest file: " + apk_name)
        return
    print("Parsing1 " + apk_name)
    # format of pairs: {activity1: {actions: action1, category: cate1 }}
    pairs = extract_activity_action(manifestPath)

    all_activity_num = len(pairs.keys())

    # save_activity_to_csv(accessbility_folder, apk_name,  pkg, all_activity_num)

    # for activity, other in pairs.items():
    #     component = pkg + '/' + activity
    #     action = pairs[activity]['actions']
    #     category = pairs[activity]['category']
    #
    #     startAct(component, action, category, pkg, apk_name, accessbility_folder, results_outputs)

    for activity, other in pairs.items():
        print(activity)
        component = defined_pkg_name + '/' + activity
        for s in other:
            action = s[0]
            category = s[1]

            status = startAct(component, action, category, apk_name, results_folder, results_outputs)
            print(status)
            if status == 'normal':
                break

        # without action and category
        startAct(component, '', '', apk_name, results_folder, results_outputs)


def get_pkgname(apk_path):
    global defined_pkg_name
    global used_pkg_name
    # changed
    cmd = "aapt dump badging %s | grep 'package' | awk -v FS=\"'\" '/package: name=/{print$2}'" % apk_path
    defined_pkg_name = subprocess.getoutput(cmd)

    launcher = subprocess.getoutput(r"aapt dump badging " + apk_path + " | grep launchable-activity | awk '{print $2}'")
    if launcher.startswith(".") or defined_pkg_name in launcher or launcher == '':
        used_pkg_name = defined_pkg_name
    else:
        used_pkg_name = launcher.replace('.' + launcher.split('.')[-1], '').split('\'')[1]


def remove_folder(apkname, decompilePath):
    folder = os.path.join(decompilePath, apkname)
    if not os.path.exists(folder):
        return
    for f in os.listdir(folder):
        if not f == 'AndroidManifest.xml':
            rm_path = os.path.join(folder, f)
            if os.path.isdir(rm_path):
                shutil.rmtree(rm_path)
            else:
                os.remove(rm_path)


def exploreActivity(new_apkpath, apk_name, results_folder, emulator, tmp_file, storydroid, dark_mode = "light_mode",
                    fontsize="normal"):
    global adb, current_font_size, current_dark_mode
    # change
    current_font_size = fontsize
    current_dark_mode = dark_mode
    adb = "adb -s %s" % (emulator)

    global tmp_dir
    tmp_dir = tmp_file

    global act_paras_file
    act_paras_file = storydroid
    current_setting = current_font_size + "_" + current_dark_mode
    decompilePath = os.path.join(results_folder, "apktool")  # Decompiled app path (apktool handled)
    results_outputs = "output/" + apk_name + "/" + pressLocations.get(adb[-13:]).get("name") + "/" + current_setting + "/googleScanner"
    installErrorAppPath = os.path.join(results_folder, "install-error-apks")

    if not os.path.exists(decompilePath):
        os.makedirs(decompilePath)
    if not os.path.exists(results_outputs):
        os.makedirs(results_outputs)
    if not os.path.exists(installErrorAppPath):
        os.makedirs(installErrorAppPath)

    ### The pkg is the real pkg

    result = installAPP(new_apkpath, apk_name, results_folder)

    if result == 'Failure':
        # Copy original app to install error folder
        copy_org_apk = "mv %s %s" % (new_apkpath, installErrorAppPath)
        subprocess.getoutput(copy_org_apk)
        # Collect the install error apks

        return

    parseManifest(new_apkpath, apk_name, results_folder, decompilePath, results_outputs)
    print("%s parsing fininshed!" % new_apkpath)
    print("cannot uninstall")
    uninstallApp(defined_pkg_name)

    # Remove the decompiled and modified resources
    # remove_folder(apk_name, decompilePath)

# extract_activity_action('/home/senchen/accessibility/apktool_outputs/wuqianwan/com.arcsoft.perfect365_2018-12-19/AndroidManifest.xml')
