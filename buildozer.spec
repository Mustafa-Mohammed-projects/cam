[app]
title = SecurePhoto Vault
package.name = securephotovault
package.domain = org.security.vault
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Dependencies
requirements = python3,kivy,cryptography,pillow,pyjnius

# Android Specifics
android.api = 33
android.minapi = 26
android.sdk = 33
android.ndk = 25b

# Permissions
android.permissions = CAMERA, USE_BIOMETRIC, READ_MEDIA_IMAGES, WRITE_EXTERNAL_STORAGE, INTERNET

# Security Configuration
android.manifest.launchMode = singleTask
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
