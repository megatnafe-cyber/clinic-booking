[app]
title = clinic booking
package.name = clinicbooking
package.domain = org.clinic
source.dir = .
source.include_exts = py,png
version = 1.0
android.api = 33
android.minapi = 21
android.ndk = 25b
p4a.branch = master
requirements = python3,kivy,requests,urllib3,idna,chardet,certifi
orientation = portrait
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
