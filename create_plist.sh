#!/bin/bash

PYTHON_PATH=$(which python)
PLIST_PATH=$(dirname $PYTHON_PATH)/Info.plist

echo '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>rumps</string>
</dict>
</plist>' > "$PLIST_PATH"

echo "Info.plist created at: $PLIST_PATH" 