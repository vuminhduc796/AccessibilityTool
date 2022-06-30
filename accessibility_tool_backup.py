import subprocess
from os.path import isfile, join
from owleyes.cnn_cam3 import owleyes_scan
from xbot.code.run_xbot import run_xbot
from guidedExplore.run_preprocess import run_deer
import os
import typer



if __name__ == '__main__':
    current_directory = os.getcwd()
    #xbot
    list_of_devices = ["phone-vertical"]
    run_xbot(list_of_devices)
    # ui checker
    apks = [f for f in os.listdir("./input") if isfile(join("./input", f))]

#    for apk in apks:
        #ui checker
        # os.system("export ANDROID_SDK_ROOT=/Users/leih/Library/Android/sdk")
        # os.system("export ANDROID_SDK=/Users/leih/Library/Android/sdk")
        # os.system("./uichecker/uicheck " + apk + " ./uichecker/rules/input.dl")
        #os.system("./uichecker/uicheck " + apk + " ./uichecker/rules/input.dl")

        #deer
        #run_deer(apk,"emulator-5554",current_directory)

        #owleye
        #owleyes_scan(apk[:-4],current_directory)



