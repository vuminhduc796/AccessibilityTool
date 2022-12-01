import os
import shutil
from os.path import isfile, join

from guidedExplore.decompile_apk import unit_decpmpile
from guidedExplore.extract_atg import batch_extract, activity_searching
from guidedExplore.extract_intent import extractIntent
from guidedExplore.extract_intent_paras import smali_intent_para_extractor
from guidedExplore.inject_apk import injectApk
from guidedExplore.instrument_apk import unit_inject
from guidedExplore.merge_deeplink_params import ParamGenerator

def unit_run_preprocess(apk_path, app_save_dir, repackage_app_save_dir, deeplinks_path, save_dir, recompiled_apks, merged_path,outmost_directory):
    # if not os.path.exists(app_save_dir):
    #     print(app_save_dir, 'not found')
    #     return

    # recompile apk
    print('recompile', apk_path)
    unit_decpmpile(apk_path, app_save_dir)

    # instrument apk
    apk = app_save_dir[app_save_dir.rindex('/') + 1:]

    repackage_app_save_apk = os.path.join(repackage_app_save_dir, apk)
    if not os.path.exists(repackage_app_save_apk):
        os.mkdir(repackage_app_save_apk)
    print(deeplinks_path)
    extractIntent(app_save_dir, deeplinks_path)


    # extract atg commented out because currently under investigation due to low coverage.

    # atg_save_dir = os.path.join(save_dir, 'activity_atg')
    # if not os.path.exists(atg_save_dir):
    #     os.mkdir(atg_save_dir)
    # batch_extract(decompiled_apks=recompiled_apks, save_dir=atg_save_dir)
    #

    # extract intent parameters
    paras_save_path = os.path.join(save_dir, 'intent_para.json')
    smali_intent_para_extractor(path=recompiled_apks, save_path=paras_save_path)

    # merge intent params and activity atgs
    params = ParamGenerator(paras_save_path)
    params.merge_deeplinks_params(deeplinks_path, merged_path)

def check_and_create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

def check_and_create_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'x') as f:
            f.close()

def clean_up_tmp(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def run_deer(apk_file, outmost_directory):

    if not apk_file.endswith('.apk'):
        print("filename invalid")
        return
    app_name = apk_file[:-4]
    print(outmost_directory)
    current_directory = os.path.join(outmost_directory, "guidedExplore/data")

    app_save_dir = current_directory + "/recompiled_apks/" + app_name
    repackage_app_save_dir = current_directory + '/repackaged_apks'

    save_dir = current_directory + "/" + app_name
    app_dir = os.path.join(outmost_directory, "input", apk_file)
    recompiled_apks = current_directory + "/recompiled_apks"
    merged_path = os.path.join(current_directory, app_name, 'deeplinks_params.json')
    deeplinks_path = os.path.join(current_directory, app_name, 'deeplinks.json')

    check_and_create_dir(current_directory)
    check_and_create_dir(current_directory + "/recompiled_apks")
    check_and_create_dir(repackage_app_save_dir)
    check_and_create_dir(current_directory + "/" + app_name)
    check_and_create_file(merged_path)
    check_and_create_file(deeplinks_path)
    clean_up_tmp(repackage_app_save_dir)
    clean_up_tmp(recompiled_apks)
    unit_run_preprocess(app_dir, app_save_dir, repackage_app_save_dir, deeplinks_path, save_dir, recompiled_apks, merged_path, outmost_directory)

    print("----------done modifying------------")

# add this for testing purposes
if __name__ == "__main__":
    # apk_file = "com.google.android.apps.maps.apk"
    # emulator = "emulator-5554"
    # outmost_directory = "/Users/yuhang/Desktop/guidedExplore"
    # login_options = "--

    # login_options = {'hasLogin': True, 'username': '', 'password': '',
    #                  'activityName': '.login.main.activities.Login', 'packageName': 'com.groupon',
    #                  'facebookLogin': False}
    # apk_file = 'groupon.apk'
    # emulator = '08221FDD4004DF'
    outmost_directory = os.getcwd().replace('/guidedExplore','')
    #
    # run_deer(apk_file, emulator, outmost_directory)
    apks = [f for f in os.listdir("../input") if isfile(join(outmost_directory + "/input", f))]
    print(apks)
    #run_deer("Firefox.apk", outmost_directory)
    for apk in apks:

        run_deer(apk, outmost_directory)


