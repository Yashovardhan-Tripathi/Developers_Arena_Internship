"""Run reproducible local checks and save their real output. Uses no cloud credentials."""
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent


def main():
    env = os.environ.copy()
    env.update(DEBUG='True', DATABASE_URL='', REDIS_URL='', USE_S3='False')
    commands = [
        (['check'], env),
        (['makemigrations', '--check', '--dry-run'], env),
        (['collectstatic', '--noinput'], env),
        (['test', '--settings=social_platform.test_settings', '--verbosity=2'], env),
    ]
    production = env.copy()
    production.update(
        DEBUG='False', SECRET_KEY='validation-only-' + 'x' * 64,
        DATABASE_URL='postgres://placeholder:placeholder@127.0.0.1:5432/placeholder',
        REDIS_URL='redis://127.0.0.1:6379/0', USE_S3='True',
        AWS_STORAGE_BUCKET_NAME='validation-placeholder',
        ALLOWED_HOSTS='example.test,healthcheck.railway.app',
        CSRF_TRUSTED_ORIGINS='https://example.test',
    )
    commands.append((['check', '--deploy'], production))
    log = [f"Local verification: {datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()}",
           f"Python: {sys.version.split()[0]}",
           "Production settings check uses placeholders only; no infrastructure connection is verified."]
    failed = False
    for args, child_env in commands:
        result = subprocess.run([sys.executable, 'manage.py', *args], cwd=ROOT, env=child_env,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding='utf-8', errors='replace')
        log.extend(['', '$ python manage.py ' + ' '.join(args), result.stdout, f'Exit code: {result.returncode}'])
        print(f"{' '.join(args)}: exit {result.returncode}", flush=True)
        failed = failed or result.returncode != 0
    (ROOT / 'docs' / 'validation.txt').write_text('\n'.join(log), encoding='utf-8')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
