#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys


def run_cmd(args: list[str]) -> None:
    subprocess.run(args, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Automate git add, commit, and push from this repository.'
    )
    parser.add_argument(
        '-m',
        '--message',
        required=True,
        help='Commit message to use for git commit.',
    )
    parser.add_argument(
        '--allow-empty',
        action='store_true',
        help='Allow creating an empty commit when there are no staged changes.',
    )
    args = parser.parse_args()

    try:
        run_cmd(['git', 'add', '-A'])

        commit_cmd = ['git', 'commit', '-m', args.message]
        if args.allow_empty:
            commit_cmd.append('--allow-empty')
        run_cmd(commit_cmd)

        run_cmd(['git', 'push'])
    except subprocess.CalledProcessError as exc:
        print(f'Command failed with exit code {exc.returncode}: {exc.cmd}', file=sys.stderr)
        return exc.returncode

    print('Deployment complete: add, commit, and push succeeded.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())