[app]
title = SecurePhoto Vault
package.name = securephotovault
package.domain = org.security.vault
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Dependencies
# Removed cryptography temporarily due to Python 3.14 compatibility issues
requirements = python3,kivy,pillow,pyjnius,openssl,cryptography

# Android Specifics
android.accept_sdk_license = True
android.allow_backup = True
android.sdk = 33
android.ndk = 25b
android.api = 33
android.minapi = 21
# Use only arm64-v8a to avoid 32-bit ARM compilation issues with Python 3.14
android.archs = arm64-v8a

# Permissions
android.permissions = CAMERA, USE_BIOMETRIC, READ_MEDIA_IMAGES, WRITE_EXTERNAL_STORAGE, INTERNET

# Security Configuration
android.manifest.launchMode = singleTask
orientation = portrait
fullscreen = 1

android.release_artifact = apk
android.keystore = 
android.keystore_passwd = 
android.keyalias = 
android.keyalias_passwd = 

[buildozer]
log_level = 2
warn_on_root = 1
