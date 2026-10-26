"""Build and check both language editions, or refresh gettext templates."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=['en', 'zh_CN'], action='append')
    parser.add_argument('--gettext', action='store_true')
    args = parser.parse_args()
    languages = args.language or ['zh_CN', 'en']
    (ROOT / 'build/logs').mkdir(parents=True, exist_ok=True)
    for language in (['en'] if args.gettext else languages):
        builder = 'gettext' if args.gettext else 'html'
        output = 'build/gettext' if args.gettext else f'build/html/{language}'
        command = [sys.executable, '-m', 'sphinx', '-E', '-b', builder,
                   '-D', f'language={language}', '-d', f'build/doctrees/{builder}/{language}',
                   '-W', '--keep-going', '-w', f'build/logs/{builder}_{language}.log',
                   'source', output]
        subprocess.run(command, cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'scripts/generate_classref.py', '--check'], cwd=ROOT, check=True)
    if not args.gettext:
        subprocess.run([sys.executable, 'scripts/check_classref.py', *languages], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
