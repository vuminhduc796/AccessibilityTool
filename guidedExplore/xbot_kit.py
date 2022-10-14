import os
import shutil
from guidedExplore.util import *
import re

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


def get_screen_size():
    cmd = "adb shell wm size"
    print(cmd)
    process = os.popen(cmd)
    output = process.read()
    m = re.search(r'(\d+)x(\d+)', output)
    if m:
        # (w,h)
        return int(m.group(1))
    return None


def clean_tmp_folder(folder):
    for f in os.listdir(folder):
        file = os.path.join(folder, f)
        # For macbook
        # os.system("chmod +x " + file)
        if os.path.isdir(file):
            shutil.rmtree(file)
        # os.remove(file)


def scan_and_return(deviceId):
    # function from xbot to click on certain button from the current screen
    time.sleep(1)

    # scan and share
    # os.system(adb + ' shell input tap 110 170')
    # 945,1650

    # os.system(adb + ' shell input tap 720 826')
    time.sleep(1)
    current_emulator = deviceId
    print(pressLocations.get(current_emulator))

    os.system('adb shell input tap ' + str(pressLocations.get(current_emulator).get("check").get("x")) + " " + str(
        pressLocations.get(current_emulator).get("check").get("y")))
    time.sleep(3)

    screensize = get_screen_size()
    # horizontal phone need higher cut in cuz more pixel
    if current_emulator == "emulator-5558":

        os.system('adb shell input tap ' + str(int(screensize) - 360) + " " + str(170))
    else:
        os.system('adb shell input tap ' + str(int(screensize) - 150) + " " + str(150))

    time.sleep(3)
    # cancel and back
    os.system('adb shell input keyevent 4')
    time.sleep(1)
    os.system('adb shell input keyevent 3')
    time.sleep(1)


def collect_results(activity, accessbility_folder, deviceId, appName):
    #  function from xbot to save the result from the device
    # print("collectResultFunc")
    scanner_pkg = 'com.google.android.apps.accessibility.auditor'
    print('Collecting scan results from device...')

    # To save issues and screenshot temporarily in order to rename.
    tmp_folder = os.path.join(accessbility_folder, deviceId)
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    '''Pull issues and rename'''
    issue_path = os.path.join(accessbility_folder, appName, 'issues')
    if not os.path.exists(issue_path):
        os.makedirs(issue_path)
    pull_results = "adb pull /data/data/%s/cache/export/ %s" % (scanner_pkg, tmp_folder)
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

    clean_results = 'adb shell rm -rf /data/data/%s/cache/export/' % (scanner_pkg)
    os.system(clean_results)

    clean_screenshots = 'adb shell rm -rf /data/data/%s/files/screenshots' % (scanner_pkg)
    os.system(clean_screenshots)
