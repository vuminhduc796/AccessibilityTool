import subprocess
from os.path import isfile, join

from xbot.code.run_xbot import run_xbot
from guidedExplore.run_preprocess import run_deer
import os

if __name__ == '__main__':
    #xbot
    list_of_devices = ["phone-vertical"]
    #run_xbot(list_of_devices)

    # ui checker
    apks = [f for f in os.listdir("./input") if isfile(join("./input", f))]
    for apk in apks:

        #os.system("./uichecker/uicheck " + apk + " ./uichecker/rules/input.dl")
        run_deer(apk,"emulator-5554")
    #deer

