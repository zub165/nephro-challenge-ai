# AGENTS.md — Nephro Challenge AI

## Mandatory rule: secrets & credentials

**NEVER hardcode passwords, API keys, tokens, OAuth client secrets, or any credential
inside source code, seed data, or migration files.** This applies to every current and
future app in this repo (backend / web / mobile) and any other project.

Enforced workflow:

1. **Store secrets only in environment files or environment variables** (`.env`, CI/CD
   secrets, VPS systemd env, etc.). Never in `.dart`, `.ts/.tsx`, `.py`, `.json`,
   `.yaml` files that get committed.
2. **`.env` files are gitignored** (see root `.gitignore`, `*.env`). Keep the repo free
   of any real secret.
3. **Commit only a `.env.example`** with placeholder/`change-me` values documenting
   every variable, including a comment saying `.env` is gitignored.
4. **Read credentials from env at runtime**, not literals:
   - Backend (Django): `os.getenv("...", default)` in `settings.py` or command modules
     (e.g. `ADMIN_PASSWORD` in `seed_data.py`). Never write a password literal in a
     management command, view, or serializer.
   - Flutter: no secrets in `constants.dart`. Use
     `String.fromEnvironment("KEY")` + `--dart-define` (or `flutter_dotenv` with a
     gitignored `.env`); pass values at build time.
   - Web (Vite): `import.meta.env.VITE_*`, real values only in gitignored
     `.env.production` / `.env.local`.
5. **Default/dev credentials are acceptable only as documented fallbacks** in
   `.env.example` / README, never in shipped code.
6. **If a secret ever enters git history, rotate it** — assume compromised.

## Repo conventions
- Backend deploys to the GoDaddy VPS by file copy (`scp`/`rsync`), NOT git. The server
  is not a repo; never run `git pull` there.
- Never run `makemigrations` on the server (Django version index-name drift); only
  `manage.py migrate` on the server, and generate migrations locally.
- Before committing, run: backend `manage.py check`, web `npm run build` (tsc), mobile
  `dart analyze` and `flutter analyze`.
- Mobile release builds: bump `appVersion`/`buildNumber` in
  `mobile/lib/config/constants.dart` and rebuild AAB + IPA to
  `mobile/releases/`.