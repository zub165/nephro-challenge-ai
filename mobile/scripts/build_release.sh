#!/usr/bin/env bash
# Build release AAB (Android) and IPA (iOS) for store submission.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Flutter pub get"
flutter pub get

ANDROID_KEYSTORE="android/upload-keystore.jks"
ANDROID_KEY_PROPS="android/key.properties"

if [[ ! -f "$ANDROID_KEY_PROPS" ]]; then
  echo "==> Creating Android upload keystore (first time only)"
  if [[ ! -f "$ANDROID_KEYSTORE" ]]; then
    keytool -genkey -v \
      -keystore "$ANDROID_KEYSTORE" \
      -keyalg RSA -keysize 2048 -validity 10000 \
      -alias upload \
      -storepass nephro_release_change_me \
      -keypass nephro_release_change_me \
      -dname "CN=Nephro Challenge AI, OU=Mobile, O=Nephro Challenge, L=US, ST=US, C=US"
  fi
  cp android/key.properties.example "$ANDROID_KEY_PROPS"
  echo "Created $ANDROID_KEY_PROPS — change passwords before production release."
fi

echo "==> Building Android App Bundle (AAB)"
flutter build appbundle --release

echo "==> AAB output: build/app/outputs/bundle/release/app-release.aab"

echo "==> Building iOS IPA (requires Xcode + signing)"
flutter build ipa --release --export-options-plist=ios/ExportOptions.plist || {
  echo "IPA build needs Apple Developer signing. Open ios/Runner.xcworkspace in Xcode,"
  echo "set Team & Bundle ID, then run: flutter build ipa --release"
}

if [[ -d build/ios/ipa ]]; then
  echo "==> IPA output: build/ios/ipa/*.ipa"
fi

echo "Done."
