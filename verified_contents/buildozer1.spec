[app]
# (str) Title of your application
title = ARIA Finance
version = 1.0

version = 1.0

# (str) Package name
package.name = ariafinance

# (str) Package domain (needed for android packaging)
package.domain = org.aria

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# CAUTION: openssl and certifi are REQUIRED for HTTPS (Render)
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,openssl,charset-normalizer,idna

# (str) Custom source folders for requirements
# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) indicates if the application should be fullscreen or not
fullscreen = 1
orientation = portrait
android.manifest.orientation = portrait
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1