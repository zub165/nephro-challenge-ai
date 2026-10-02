#!/usr/bin/env bash
# Deploy Flutter Web + legal pages + medical/animation assets to GitHub Pages.
# Live app: https://zub165.github.io/nephro-challenge-ai/app/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MOBILE="$ROOT/mobile"
WEB_PUBLIC="$ROOT/web/public"
SITE="$ROOT/website"
API_URL="${API_BASE_URL:-https://nephro-api.schedulemygroup.com/api}"
BASE_HREF="/nephro-challenge-ai/app/"

cd "$MOBILE"
flutter pub get
flutter build web --release --base-href="$BASE_HREF" \
  --dart-define=API_BASE_URL="$API_URL"

WORKDIR="$(mktemp -d)"
cleanup() { rm -rf "$WORKDIR"; git -C "$ROOT" worktree prune >/dev/null 2>&1 || true; }
trap cleanup EXIT

cd "$ROOT"
git fetch origin gh-pages
git worktree add --detach "$WORKDIR" origin/gh-pages
git -C "$WORKDIR" checkout -B gh-pages

# Keep lesson media at the same public URLs.
mkdir -p "$WORKDIR/animations" "$WORKDIR/medical" "$WORKDIR/app"
if [[ -d "$WEB_PUBLIC/animations" ]]; then
  rsync -a --delete "$WEB_PUBLIC/animations/" "$WORKDIR/animations/"
fi
if [[ -d "$WEB_PUBLIC/medical" ]]; then
  rsync -a --delete "$WEB_PUBLIC/medical/" "$WORKDIR/medical/"
fi

rsync -a --delete "$MOBILE/build/web/" "$WORKDIR/app/"
cp "$SITE/index.html" "$WORKDIR/index.html"
cp "$SITE/delete.html" "$WORKDIR/delete.html"
cp "$SITE/.nojekyll" "$WORKDIR/.nojekyll"
cp "$WEB_PUBLIC/privacy.html" "$WORKDIR/privacy.html"
cp "$WEB_PUBLIC/support.html" "$WORKDIR/support.html"
# Favicon for marketing pages
if [[ -f "$MOBILE/web/favicon.png" ]]; then
  cp "$MOBILE/web/favicon.png" "$WORKDIR/favicon.png"
fi
if [[ -f "$WEB_PUBLIC/favicon.svg" ]]; then
  cp "$WEB_PUBLIC/favicon.svg" "$WORKDIR/favicon.svg"
fi

# SPA-style fallback: unknown paths go to the Flutter app.
cat > "$WORKDIR/404.html" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Nephro Challenge AI</title>
  <meta http-equiv="refresh" content="0; url=/nephro-challenge-ai/app/" />
  <script>location.replace('/nephro-challenge-ai/app/');</script>
</head>
<body>Redirecting to the Flutter app…</body>
</html>
HTML

cd "$WORKDIR"
git add -A
if git diff --cached --quiet; then
  echo "No GitHub Pages changes."
  exit 0
fi
git -c user.useConfigOnly=true commit -m "Deploy Flutter web 1.3.10 (React-style menu + admin)" || \
  git commit -m "Deploy Flutter web 1.3.10 (React-style menu + admin)"
git push origin HEAD:gh-pages
echo "Published https://zub165.github.io/nephro-challenge-ai/app/"
