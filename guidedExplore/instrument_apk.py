import os
from guidedExplore import inject_apk

def batch_inject(apk_dir, save_dir, re_packaged_dir, deeplinks_path):
    for root, dirs, files in os.walk(apk_dir):
        for apk in files:
            if not str(apk).endswith('.apk'):
                continue
            apk_path = os.path.join(root, apk)
            app_save_dir = os.path.join(save_dir, apk)
            re_packaged_apk = os.path.join(re_packaged_dir, apk)
            if os.path.exists(app_save_dir) and os.path.exists(re_packaged_apk):
                print(apk + 'skip')
                continue
            unit_inject(app_save_dir, re_packaged_apk, deeplinks_path=deeplinks_path)





# /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/hhuu0025/.android/debug.keystore /Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/bilibili_v1.16.2_apkpure.com.apk

#  /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks activityMining/apkSignedKey --ks-key-alias key0 --ks-pass pass:123456 --key-pass pass:123456 --v4-signing-enabled false  /Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk

# /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/hhuu0025/.android/debug.keystore --ks-pass pass:android --key-pass pass:android  /Users/h
# huu0025/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk


def unit_inject(app_save_dir, re_packaged_apk, deeplinks_path, outmost_directory):
    # print('Start apktool')
    # cmd1 = 'apktool d ' + apk_path + ' -f -o ' + app_save_dir
    # # os.system(cmd1)

    print('run inject apk')
    inject_apk.injectApk(app_save_dir, deeplinks_path)



if __name__ == '__main__':
    re_packaged_dir = r'data/repackaged_apks'
    apk_dir = r'data/apks'
    save_dir = r'data/recompiled_apks'
    deeplinks_path = r'data/deeplinks.json'
    # batch_inject(apk_dir, save_dir, re_packaged_dir, deeplinks_path)
    # batch_sign_apks(re_packaged_dir)
    app_save_dir = r'data/recompiled_apks/fluxi'
    unit_inject(app_save_dir, re_packaged_dir + '/test.apk', deeplinks_path)

    # unit_sign_APK(re_packaged_dir + '/test.apk')
