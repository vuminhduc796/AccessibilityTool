"""
This is an entry for Accessibility Tool
"""
import os
from os.path import isfile, join
import typer
from pathlib import Path
import config.config as sys_config
from guidedExplore.run_preprocess import run_deer
from owleyes.cnn_cam3 import owleyes_scan
from xbot.code.run_xbot import run_xbot
app=typer.Typer(help="Android Accessibility Tool")
current_directory= os.getcwd()
@app.command("detect")
def detect_file_availability_issues(
        apk_path:Path = typer.Option('./input',"--input","--i",
                              exists=True,
                              file_okay=False,
                              dir_okay=True,
                              writable=False,
                              readable=True,
                              help="The path of files that are being detected"
                              ),
        device:str = typer.Option(sys_config.config_content["emulators"]["default"],"--device","--d",help="Uses device to test accessibility issues")
):

        list_of_devices = [d.strip() for d in device.split(',')]
        typer.secho("========Start running Xbot========", fg=typer.colors.MAGENTA)
        run_xbot(list_of_devices,apk_path)
        typer.secho("========Xbot Finished========",fg=typer.colors.MAGENTA)
        # ui checker
        typer.secho("========Start running UI checker========",fg=typer.colors.MAGENTA)
        apks = [f for f in os.listdir(apk_path) if isfile(join("./input", f))]
        for apk in apks:
            # ui checker
            os.system("export ANDROID_SDK_ROOT="+sys_config.config_content["sdk_platform_path"])
            os.system("export ANDROID_SDK="+sys_config.config_content["sdk_platform_path"])
            #os.system("./uichecker/uicheck " + str(apk_path.absolute())+"/"+apk + " ./uichecker/rules/input.dl")
            typer.secho("========UI checker Finished========",fg=typer.colors.MAGENTA)
            ##deer
            typer.secho("========Start running deer========",fg=typer.colors.MAGENTA)
            if list_of_devices[0] in sys_config.config_content['emulators']:
                emulator_name = sys_config.config_content['emulators'][list_of_devices[0]]["name"]
            else:
                emulator_name=list_of_devices[0]
            run_deer(apk,emulator_name,current_directory)
            typer.secho("========Deer Finished========",fg=typer.colors.MAGENTA)
            typer.secho("========Start running owleye========",fg=typer.colors.MAGENTA)
            # owleye
            owleyes_scan(apk[:-4],current_directory)
            typer.secho("========OwlEye Finished========",fg=typer.colors.MAGENTA)
@app.command("replay")
def replay():
    pass
@app.command("config")
def config():
    pass
if __name__ == '__main__':
    app()