[app]
title = clinic booking
package.name = clinicbooking
package.domain = org.clinic
source.dir = .
source.include_exts = py,png
version = 1.0
p4a.branch = v2024.01.21
android.api = 31
android.minapi = 21
requirements = python3,kivy,requests,urllib3,idna,chardet,certifi
orientation = portrait
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
