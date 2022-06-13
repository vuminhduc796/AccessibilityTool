import subprocess
from os.path import isfile, join

from xbot.code.run_xbot import run_xbot
import os

if __name__ == '__main__':
    # #xbot
    # list_of_devices = ["phone-vertical", "tablet-horizontal"]
    # run_xbot(list_of_devices)

    # ui checker
    apks = [f for f in os.listdir("./input") if isfile(join("./input", f))]
    for apk in apks:

        os.system("./uichecker/uicheck " + apk + " ./uichecker/rules/input.dl")

    #deer

