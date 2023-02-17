# Android App Usability & Accessibility Testing Tool 
Accessibility Tool is an automated Android testing tool that is integrated multiple modules to report usability and accessibility issues. The main objective is to automatically detect issues of given APKs on multiple devices with multiple device settings.


https://user-images.githubusercontent.com/68264720/219286070-d0cb3874-834a-48c7-be6f-c7936b672f21.mp4


👨🏻‍💻 Following features have been provided by our tool:

- Generating screenshots and transition graphs for testing application.
- Generating accessibility reports for each screen in the application via Google Accessibility Scanner.
- Reporting bug and crash logs.
- Detecting GUI visual defects via Owleyes.

ℹ️ Please check out our wiki page for more information.

## Installations
We have included the full instruction in our Wiki page.

1. Clone the repo into your local machine ✅
2. Set up your local configurations in `config.yml` ✅
3. Install all required packages `conda create --name <env> --file requirement.txt` ✅
4. Make sure all [dependencies](https://github.com/vuminhduc796/AccessibilityTool/wiki/Dependencies) are met and [set up the emulators](https://github.com/vuminhduc796/AccessibilityTool/wiki/Emulators-Set-Up) ✅
5. Add your APKs into the `./input` folder ✅
6. Start a complete scan with `python accessibility_tool.py detect --d phone-vertical --all` ✅

## Usages
### Help page

```bash
# help
python accessibility_tool.py --help
```

```
Usage: accessibility_tool.py [OPTIONS] COMMAND [ARGS]...

  Android Accessibility Tool

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  config    Manage config.
  detect    Detect Accessibility issues.
  emulator  Manage emulators.
  replay    Replay bugs.
```


### Issue Detection


```bash
# help
python accessibility_tool.py detect --help

# all tools with vertical phone and vertical tablet scan.
python accessibility_tool.py detect --input ./input --all

# all tools with vertical phone.
python accessibility_tool.py detect --device emulator-5554 --all

# render the frontend without re-scaning.
python accessibility_tool.py detect --device emulator-5554 --frontend
```

```
Usage: accessibility_tool.py detect [OPTIONS]

  Detect Accessibility issues.

Options:
  --input, --i DIRECTORY        The path of files that are being detected
                                [default: /Users/vuminhduc796/PycharmProjects/
                                AccessibilityTool/input]
  --device, --d TEXT            Uses device to test accessibility issues
                                [default: phone-vertical, phone-horizontal]
  --screenshot_issue, --s       Uses OwlEye to generate screenshots of errors
  --all, --a                    Uses all the tools(Xbot, UI checker, deer and
                                OwlEye)
  --frontend, --display_result  Uses all the tools(Xbot, UI checker, deer and
                                OwlEye)
  --help                        Show this message and exit.
```

**choose a tool to detect**: [REQUIRED] `--all, --screenshot_issue, --frontend`

**--input**: [OPTIONAL] the directory where apps are. Default is set to `./input`.

**--device**: [OPTIONAL] the device to test apps, multiple devices are supported. Default is set to vertical phone and vertical tablet.


### Edit Configuration

```sh
python accessibility_tool.py config --help
```
```
Usage: accessibility_tool.py config [OPTIONS] COMMAND [ARGS]...

  Manage config.

Options:
  --help  Show this message and exit.

Commands:
  auto_login  Set up User credentials and apk information for auto login.
  emulator    Set up Android emulators for testing App Accessibility.

```
\_**config/config.yml** [REQUIRED]\_

You need to modify **config.yml**. 
[Visit our Wiki page for more information](https://github.com/vuminhduc796/AccessibilityTool/wiki/Config-File).

```
aapt: /Users/username/Library/Android/sdk/build-tools/30.0.3/aapt
apk_signer: /Users/username/Library/Android/sdk/build-tools/30.0.3/apksigner sign
  --ks /Users/username/.android/debug.keystore --ks-pass pass:android --key-pass
  pass:android
arm64: 'true'
auto_login:
  activity: .ui.authentication.mediaauth.AuthActivity
  method: facebook
  packageName: com.Alltrails.alltrails
dark_mode: 'false'
default_facebook:
  password: 'password'
  username: 'username'
emulators:
  alias:
    phone: emulator-5554
    phone-horizontal: emulator-5558
    phone-vertical: emulator-5554
    tablet-horizontal: emulator-5556
    tablet-vertical: emulator-5560
  default:
  - phone-vertical
  - phone-horizontal
  phone-horizontal:
    name: emulator-5558
  phone-vertical:
    name: emulator-5554
  tablet-horizontal:
    name: emulator-5556
  tablet-vertical:
    name: emulator-5560
finished: 'false'
font_size: normal
java_home_path: /Users/username/Library/Java/JavaVirtualMachines/liberica-1.8.0_312/jre
sdk_platform_path: /Users/username/Library/Android/sdk
updated: ''
zip_align: /Users/username/Library/Android/sdk/build-tools/30.0.3/zipalign

```

\_**emulator** [OPTIONAL]\_

- **--add, --a**
- **--delete, --d**

````sh
python accessibility_tool.py config emulator --help
````

```
Usage: accessibility_tool.py config emulator [OPTIONS]

  Set up Android emulators for testing App Accessibility.

Options:
  --add, --a TEXT     Format:[alias:name], adds an [alias] for the emulator
                      [name]
  --delete, --d TEXT  Format:[alias], delete an [alias]
  --help              Show this message and exit.
```

\_**auto-login** [OPTIONAL]\_

- **--facebook, --a**
- **--pass, --p**
- **--delete, --d**

```sh
 python accessibility_tool.py config auto_login --help
```

```
Usage: accessibility_tool.py config auto_login [OPTIONS]

  Set up User credentials and apk information for auto login.

Options:
  --pass, --p TEXT      Format:[username:password:activity:package_name], set
                        up [username] , [password], [activity] and
                        [package_name] for the apk in the config file.
  --facebook, --f TEXT  Format:[activity:package_name], set up [activity] and
                        [package_name] for the apk in the config file.
  --setting TEXT        Format:[username:password], set up default [username]
                        and [password] for loging in to the facebook.
  --delete, --d         Deletes auto-login configs.
  --help                Show this message and exit.

```

```sh
python accessibility_tool.py config auto-login --help
python accessibility_tool.py config auto-login --facebook MainActivity:package_name 
python accessibility_tool.py config auto-login --pass 123456:123456:MainActivity:package_name
python accessibility_tool.py config auto-login --setting 123456:123456 # default username and password for facebook

#remove
python accessibility_tool.py config auto-login --delete
python accessibility_tool.py config auto-login --d
```
# Feedback 
Has any feedback? Please reach out to us at vuminhduc796@gmail.com.

# Coming Soon 🚀

- Replay bugs on emulators.
- Input generation techniques.
