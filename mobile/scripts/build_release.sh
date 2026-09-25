#!/usr/bin/env bash
# Build release AAB (Android) and IPA (iOS) for store submission.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Flutter pub get"
flutter pub get

ANDROID_KEYSTORE="android/upload-keystore.jks"
ANDROID_KEY_PROPS="android/key.properties"

if [[ ! -f "$ANDROID_KEY_PROPS" ]]; then
  echo "==> android/key.properties is missing" >&2
  echo "Create it from android/key.properties.example and fill in the upload keystore" >&2
  echo "values. Passwords must come from your password manager or CI secrets, never" >&2
  echo "from a committed file. See backend/.env.example for the same policy." >&2
  exit 1
fi

if [[ ! -f "$ANDROID_KEYSTORE" ]]; then
  echo "==> Upload keystore $ANDROID_KEYSTORE not found" >&2
  echo "Generate it once with keytool using a password from your secret store, then" >&2
  echo "record the same values in $ANDROID_KEY_PROPS. Do not commit either file." >&2
  exit 1
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
