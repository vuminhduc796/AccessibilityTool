# encoding: utf8
import uiautomator2 as u2
import time
from difflib import SequenceMatcher
import requests
import os
from pyaxmlparser import APK
import subprocess
import xml.etree.ElementTree as ET
from config.config import inform_update_deer


def connectionAdaptor(phoneDevice, tabletDevice):
    try:
        d1 = u2.connect(phoneDevice)
        d2 = u2.connect(tabletDevice)
        d1.app_list()
        return d1, d2, True
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return None, None, False


def installApk(apkPath, device=None, reinstall=True):
    print(apkPath)
    packageName, mainActivity = getPackageByApk(apkPath)
    # check if installed
    prefixCmd = 'adb '
    if device is not None:
        print('device: ' + device)
        prefixCmd = prefixCmd + '-s ' + device

    command1 = prefixCmd + ' shell pm list packages -3'
    packages = subprocess.check_output(command1, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    packages = packages.replace('package:', '').strip()
    packages = packages.replace('\r', '').strip()
    packages = packages.split('\n')
    if packageName in packages:
        if not reinstall:
            print(packageName + ' has installed')
            return 0, packageName, mainActivity

        print(packageName + ' has installed, begin to uninstall it')
        command2 = prefixCmd + ' uninstall ' + packageName
        out = subprocess.check_output(command2, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        print('uninstall success')

    # begin to install apk


    command3 = prefixCmd + ' install -t ' + apkPath
    # os.system(command3)
    try:
        out = subprocess.check_output(command3, shell=True, stderr=subprocess.STDOUT, timeout=25).decode('utf-8')
        print('install ' + apkPath + ' success')
        return 0, packageName, mainActivity
    except subprocess.CalledProcessError as e:
        print('install apk error: ' + apkPath)
        out = e.output.decode('utf-8')
        print(out)
        # 'adb: failed to install apks/VidMate.apk: Failure [INSTALL_FAILED_ALREADY_EXISTS: Attempt to re-install com.nemo.vidmate without first uninstalling.]
        return 1, packageName, mainActivity
    except FileNotFoundError:
        print('file not found: ' + apkPath)
        return 1, packageName, mainActivity
    except subprocess.TimeoutExpired:
        print('cmd timeout， install fail')
        return 1, packageName, mainActivity


def getPackageByApk(apkPath):
    apkf = APK(apkPath)
    package = apkf.get_package()
    mainActivity = apkf.get_main_activity()
    return package, mainActivity


def getActivityPackage(d):
    isLauncher = False
    try:
        d_current = d.app_current()
    except OSError as e:
        print(e)
        return None, None, None
    d_package = d_current['package']
    d_activity = d_current['activity']
    if 'android' in d_activity and 'Launcher' in d_activity:
        isLauncher = True
    d_activity = d_activity[d_activity.rindex('.') + 1:]
    return d_activity, d_package, isLauncher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def xmlScreenSaver(saveDir, xml1, xml2, img1, img2, activity1, activity2):
    if img1 is None or img2 is None:
        print('none img, save fail, return')
        return

    t = int(time.time())
    xml1Name = 'phone_' + str(t) + '_' + activity1 + '.xml'
    img1Name = 'phone_' + str(t) + '_' + activity1 + '.png'
    xml1Path = os.path.join(saveDir, xml1Name)
    img1Path = os.path.join(saveDir, img1Name)

    # name both with activity1
    xml2Name = 'tablet_' + str(t) + '_' + activity1 + '.xml'
    img2Name = 'tablet_' + str(t) + '_' + activity1 + '.png'
    xml2Path = os.path.join(saveDir, xml2Name)
    img2Path = os.path.join(saveDir, img2Name)
    with open(xml1Path, 'a', encoding='utf8') as f1, open(xml2Path, 'a', encoding='utf8') as f2:
        f1.write(xml1)
        f2.write(xml2)
        img1.save(img1Path)
        img2.save(img2Path)


def xmlScreenSaver_single(saveDir, xml1, img1, activity1):
    if img1 is None:
        print('none img, save fail, return')
        return

    t = int(time.time())
    xml1Name = 'phone_' + str(t) + '_' + activity1 + '.xml'
    img1Name = 'phone_' + str(t) + '_' + activity1 + '.png'
    xml1Path = os.path.join(saveDir, xml1Name)
    img1Path = os.path.join(saveDir, img1Name)

    with open(xml1Path, 'a', encoding='utf8') as f1:
        f1.write(xml1)
        img1.save(img1Path)


def saveScreenshot(d, ss_path, activity_name):
    try:
        img = d.screenshot()
        img.save(ss_path + activity_name + '.png')
        img.close()
        inform_update_deer()
        return img
    except Exception as e:
        print( e.args)
        return None


# return value 0 success, 1 install fail, 2 no the same texts, 3 time out, 4 fail others, 5 no tablet adaption
def apksUninstall(apkPath, d1, d2, d1_packages, d2_packages):
    # 0 success, 1 install fail
    packageName, mainActivity = getPackageByApk(apkPath)
    # d1_packages = d1.app_list()
    # d2_packages = d2.app_list()
    if packageName in d1_packages:
        d1.app_stop(packageName)
        d1.app_uninstall(packageName)
        print('uninstall ' + packageName)
    if packageName in d2_packages:
        d2.app_stop(packageName)
        d2.app_uninstall(packageName)
        print('uninstall ' + packageName)

    return 0


def uninstallApks():
    apksDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    device1Id = 'cb8c90f4'
    device2Id = 'R52RA0C2MFF'
    log = r'log.txt'
    delimiter = ' ||| '
    apks = {}
    index = 0

    d1, d2, connectStatus = connectionAdaptor(device1Id, device2Id)
    while not connectStatus:
        d1, d2, connectStatus = connectionAdaptor(device1Id, device2Id)

    d1_packages = d1.app_list()
    d2_packages = d2.app_list()

    with open(log, 'a+', encoding='utf8') as f:
        for root, dirs, files in os.walk(apksDir):
            for file in files:
                if file.endswith('.apk') or file.endswith('.xapk'):
                    print('apk ' + str(index))
                    index += 1
                    if index <= 1253:
                        continue
                    filePath = os.path.join(root, file)

                    try:
                        ret = apksUninstall(filePath, d1, d2, d1_packages, d2_packages)
                    except StopIteration:
                        print('time out ' + file)
                        apks[file] = 3
                        f.write(file + delimiter + '3' + '\n')
                    except Exception:
                        print('fail other ' + file)
                        apks[file] = 4
                        f.write(file + delimiter + '4' + '\n')


def uninstallApks_single(apk_dir, deviceId):
    log = r'log.txt'
    delimiter = ' ||| '
    apks = {}
    index = 0

    d1 = u2.connect(deviceId)
    d1_packages = d1.app_list()

    with open(log, 'a+', encoding='utf8') as f:
        for root, dirs, files in os.walk(apk_dir):
            for file in files:
                if file.endswith('.apk') or file.endswith('.xapk'):
                    print('apk ' + str(index))
                    index += 1
                    filePath = os.path.join(root, file)

                    try:
                        packageName, mainActivity = getPackageByApk(filePath)
                        if packageName in d1_packages:
                            d1.app_stop(packageName)
                            d1.app_uninstall(packageName)
                            print('uninstall ' + packageName)
                    except StopIteration:
                        print('time out ' + file)
                        apks[file] = 3
                        f.write(file + delimiter + '3' + '\n')
                    except Exception:
                        print('fail other ' + file)
                        apks[file] = 4
                        f.write(file + delimiter + '4' + '\n')

def search_elements_from_XMLElement(source, target):
    root = ET.fromstring(source)
    for node in root.iter('node'):
        if node.attrib['clickable'] == 'false':
            continue
        node_text = node.attrib['text'].lower()
        if target.lower() in node_text:
            return node.attrib['resource-id']
    # print('not found')
    # seach for unclickable if not found
    for node in root.iter('node'):
        if node.attrib['clickable'] == 'false':
            node_text = node.attrib['text'].lower()
            if target.lower() in node_text:
                return node.attrib['resource-id']

    return None

def search_input_from_XMLElement(source, target):
    root = ET.fromstring(source)
    for node in root.iter('node'):
        # print(node.attrib['text'])
        if node.attrib['class'] != 'android.widget.EditText':
            if not ('Text' in node.attrib['class'] and node.attrib['focusable'] == 'true' and node.attrib['clickable'] == 'true'):
                continue
        node_text = node.attrib['text'].lower()
        id_text = node.attrib['resource-id'].lower()
        if target.lower() in node_text or target.lower() in id_text:
            return node.attrib['resource-id']
    return None

if __name__ =='__main__':
    saveDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    maxLen = 100

    apksDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    device1Id = '192.168.56.104'
    #uninstallApks_single(apksDir, device1Id)
