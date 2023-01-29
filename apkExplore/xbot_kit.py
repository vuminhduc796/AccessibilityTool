import os
import shutil
import re
import subprocess
import time

pressLocations = {
    "emulator-5554": {
        "name": "phone-vertical",
        "check": {
            "x": 300,
            "y": 300
        },
        "share": {
            "x": 1221,
            "y": 279
        },

    },
    "emulator-5558": {
        "name": "phone-horizontal",
        "check": {
            "x": 300,
            "y": 300
        },
        "share": {
            "x": 2817,
            "y": 233
        },
    },
    "emulator-5556": {
        "name": "tablet-horizontal",
        "check": {
            "x": 300,
            "y": 300
        },
        "share": {
            "x": 2376,
            "y": 88
        },
    },
    "emulator-5560": {
        "name": "tablet-vertical",
        "check": {
            "x": 300,
            "y": 300
        },
        "share": {
            "x": 1680,
            "y": 112
        },
    },
}

currentIndex = 0



def get_screen_size(adb_command):
    cmd = adb_command + "shell wm size"
    # print(cmd)
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


def scan_and_return(deviceId, activity, output_dir, device, numberedActName):
    # function from xbot to click on certain button from the current screen

    # scan and share
    # os.system(adb + ' shell input tap 110 170')
    # 945,1650

    # os.system(adb + ' shell input tap 720 826')
    time.sleep(1)
    current_emulator = deviceId
    # print(pressLocations.get(current_emulator))
    if 'emulator' not in current_emulator:
        current_emulator = 'emulator-5554'
    adb_command = 'adb -s ' + current_emulator + ' '
    os.system(adb_command + 'shell input tap ' + str(pressLocations.get(current_emulator).get("check").get("x")) + " " + str(
        pressLocations.get(current_emulator).get("check").get("y")))
    time.sleep(3)

    screensize = get_screen_size(adb_command)
    # horizontal phone need higher cut in cuz more pixel
    if current_emulator == "emulator-5558":

        os.system(adb_command + 'shell input tap ' + str(int(screensize) - 360) + " " + str(170))
    elif screensize is not None:
        os.system(adb_command + 'shell input tap ' + str(int(screensize) - 150) + " " + str(150))
    else:
        os.system(adb_command + 'shell input tap ' + str(1440 - 150) + " " + str(150))

    time.sleep(3)

    os.system(adb_command + 'shell input keyevent 4')
    time.sleep(1)

    # cancel and back

    isHavingResult = collect_results(activity, output_dir, device, numberedActName)
    if isHavingResult:
        os.system(adb_command + 'shell input keyevent 4')
        time.sleep(1)
    # os.system('adb shell input keyevent 3')
    # time.sleep(1)


def collect_results(activity, output_dir, device, numberedActName):

    #  function from xbot to save the result from the device
    # print("collectResultFunc")
    scanner_pkg = 'com.google.android.apps.accessibility.auditor'
     # print('Collecting scan results from device...')
    adb_command = "adb -s " + device.serial
    # To save issues and screenshot temporarily in order to rename.
    tmp_folder = os.path.join(output_dir, "tmp")
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    '''Pull issues and rename'''
    isHavingResult = extract_issue(activity, adb_command, numberedActName, output_dir, scanner_pkg, tmp_folder)

    '''Pull screenshot and rename'''
    screenshot_path_act = os.path.join(output_dir,'activity_screenshots', activity)
    if not os.path.exists(screenshot_path_act):
        os.makedirs(screenshot_path_act)

    pull_screenshots = adb_command + " pull /data/data/%s/files/screenshots/ %s" % (scanner_pkg, tmp_folder)
    os.system(pull_screenshots)

    screenshot_path_tmp = tmp_folder + "/screenshots"
    if not os.path.exists(screenshot_path_tmp):
        os.makedirs(screenshot_path_tmp)
    for img in os.listdir(screenshot_path_tmp):
        if not img.endswith('thumbnail.png'):
            cmd = 'mv "%s/%s" "%s/%s.png"'%(screenshot_path_tmp,img,screenshot_path_act,numberedActName)
            os.system(cmd)
    clean_tmp_folder(tmp_folder)
    return isHavingResult

def clean_up_scanner_data(adb_command, scanner_pkg):
    clean_results = adb_command + ' shell rm -rf /data/data/%s/cache/export/' % scanner_pkg
    os.system(clean_results)
    clean_screenshots = adb_command + ' shell rm -rf /data/data/%s/files/screenshots' % scanner_pkg
    os.system(clean_screenshots)


def extract_issue(activity, adb_command, numberedActName, output_dir, scanner_pkg, tmp_folder):
    issue_path = os.path.join(output_dir, "issues")
    if not os.path.exists(issue_path):
        os.makedirs(issue_path)

    pull_results = adb_command + " pull /data/data/%s/cache/export/ %s" % (scanner_pkg, tmp_folder)
    # os.system(pull_results)
    result = subprocess.run(pull_results, shell=True, stdout=subprocess.PIPE)
    if 'error' in result.stdout.decode("utf-8"):
        isHavingResult = False
    else:
        isHavingResult = True

    zip_folder = os.path.join(tmp_folder + "/export")
    if os.path.exists(zip_folder):
        print(os.listdir(zip_folder))
        for zip in os.listdir(zip_folder):
            if not zip.endswith('.zip'):
                os.system('rm "%s/%s"' % (zip_folder, zip))
        for zip in os.listdir(zip_folder):
            if zip.endswith('.zip'):
                os.system('mv "%s/%s" "%s/tmp.zip"' % (zip_folder, zip, zip_folder))
                cmd = 'unzip -o "%s/tmp.zip" -d "%s"' % (zip_folder, zip_folder)
                os.system(cmd)
                os.system('rm "%s/tmp.zip"' % zip_folder)
        for f in os.listdir(zip_folder):
            folder = os.path.join(issue_path, activity)
            print(folder)
            if not os.path.exists(folder):
                os.makedirs(folder)
            if f.endswith('.png'):
                mv_cmd = 'mv "%s" "%s/%s.png"' % (os.path.join(zip_folder, f), folder, numberedActName)
                os.system(mv_cmd)
            if f.endswith('.txt'):
                mv_cmd = 'mv "%s" "%s/%s.txt"' % (os.path.join(zip_folder, f), folder, numberedActName)
                os.system(mv_cmd)
                # os.system('mv "%s/%s" "%s/%s.zip"' % (zip_folder, zip, issue_path, activity))
    clean_tmp_folder(tmp_folder)
    return isHavingResult



