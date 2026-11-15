#!/usr/bin/env python3
"""Helper for fetching, editing, and publishing existing plan text.

Uses gh for every GitHub operation and the Python standard library otherwise.
It does not decide which comments to edit or create new comments.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


STATE = '.plan-helper.json'


def save_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def api(endpoint, destination, method='GET', payload=None, paginate=False):
    command = ['gh', 'api', endpoint, '--hostname', 'github.com', '--method', method]
    if paginate:
        command += ['--paginate', '--slurp']
    if payload is not None:
        command += ['--input', str(payload)]
    with destination.open('w') as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        raise RuntimeError(f'{method} {endpoint}: {result.stderr.strip()}')
    return json.loads(destination.read_text())


def load(directory):
    state = json.loads((directory / STATE).read_text())
    if state.get('format') != 1:
        raise RuntimeError(f'{directory}: unsupported helper state format')
    return state


def endpoint(state, entry):
    base = f"repos/{state['repo']}/issues"
    if entry['comment_id'] is None:
        return f"{base}/{state['number']}"
    return f"{base}/comments/{entry['comment_id']}"


def file_name(body, comment_id, taken):
    """Name a comment's file after its first heading, e.g. comment-design.md, unique within the issue."""
    heading = next((line.lstrip('#').strip() for line in body.splitlines() if line.startswith('#')), '')
    slug = re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')
    if len(slug) > 40:
        slug = slug[:40].rsplit('-', 1)[0] or slug[:40]
    base = f'comment-{slug}' if slug else f'comment-{comment_id}'
    name, count = base, 1
    while name in taken:
        count += 1
        name = f'{base}-{count}'
    taken.add(name)
    return name + '.md'


def describe(entry):
    return 'issue body' if entry['comment_id'] is None else f"comment {entry['comment_id']}"


def pending(directory, state):
    changes = []
    for entry in state['entries']:
        text = (directory / entry['file']).read_text()
        if text != entry['original']:
            changes.append({'directory': directory, 'state': state,
                            'entry': entry, 'text': text})
    return changes


def fetch(args):
    session = args.session or os.environ.get('CLAUDE_CODE_SESSION_ID') or os.environ.get('CODEX_THREAD_ID')
    if not session or not re.fullmatch(r'[A-Za-z0-9_.-]+', session):
        raise RuntimeError('Set --session when no usable agent session ID is available.')
    plans = []
    jobs = []
    for reference in dict.fromkeys(args.references):
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)#([1-9][0-9]*)', reference)
        if not match:
            raise RuntimeError(f'Expected OWNER/REPO#NUMBER, got {reference!r}')
        owner, repo, number = match.groups()
        directory = Path('/tmp') / f'plan-{session}-{owner}-{repo}-{number}' / 'helper'
        if (directory / STATE).exists() and pending(directory, load(directory)):
            raise RuntimeError(f'{directory}: unpublished edits exist; finish them before fetching again.')
        if not (directory / STATE).exists() and directory.exists() and any(directory.glob('*.md')):
            raise RuntimeError(f'{directory}: existing Markdown has no helper baseline; use another session ID.')
        raw = directory / '.responses'
        raw.mkdir(parents=True, exist_ok=True)
        base = f'repos/{owner}/{repo}/issues/{number}'
        jobs += [(base, raw / 'issue.json', False),
                 (base + '/comments?per_page=100', raw / 'comments.json', True)]
        plans.append((directory, f'{owner}/{repo}', int(number)))

    # Read independent issues and comment lists together; install baselines only after all reads succeed.
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda job: api(job[0], job[1], paginate=job[2]), jobs))
    for index, (directory, repo, number) in enumerate(plans):
        issue, pages = results[index * 2:index * 2 + 2]
        entries = [{'file': 'body.md', 'comment_id': None, 'original': issue.get('body') or ''}]
        taken = {'body'}
        for page in pages:
            for comment in page:
                body = comment.get('body') or ''
                entries.append({'file': file_name(body, comment['id'], taken),
                                'comment_id': comment['id'], 'original': body})
        if (directory / STATE).exists():
            # Names follow headings, which may have changed; drop the previous fetch's files first.
            for old in load(directory)['entries']:
                (directory / old['file']).unlink(missing_ok=True)
                (directory / (old['file'] + '.live')).unlink(missing_ok=True)
        for entry in entries:
            (directory / entry['file']).write_text(entry['original'])
        save_json(directory / STATE, {'format': 1, 'repo': repo, 'number': number, 'entries': entries})
        print(f'{repo}#{number}: {directory} ({len(entries)} editable files)')


def collect(directories):
    changes = []
    seen = set()
    for directory in dict.fromkeys(Path(value).expanduser().resolve() for value in directories):
        state = load(directory)
        for item in pending(directory, state):
            target = endpoint(state, item['entry'])
            if target in seen:
                raise RuntimeError(f'Duplicate target in the selected directories: {target}')
            seen.add(target)
            changes.append(item)
    return changes


def report(args):
    changes = collect(args.directories)
    for item in changes:
        path = item['directory'] / item['entry']['file']
        print(f'{path} ({describe(item["entry"])}): {len(item["entry"]["original"])} -> {len(item["text"])} characters')
        if args.command == 'preview':
            before = item['entry']['original'].splitlines(keepends=True)
            after = item['text'].splitlines(keepends=True)
            print(''.join(difflib.unified_diff(before, after, fromfile=str(path) + ' (fetched)',
                                             tofile=str(path) + ' (edited)')), end='\n')
    if not changes:
        print('No pending edits.')


def current(item):
    entry = item['entry']
    destination = item['directory'] / '.responses' / (entry['file'] + '.current.json')
    data = api(endpoint(item['state'], entry), destination)
    return data.get('body') or ''


def check(item, live):
    if live not in (item['entry']['original'], item['text']):
        raise RuntimeError(f"Concurrent edit: {item['directory'] / item['entry']['file']}; "
                           'run rebase, merge the .live file into the edit, and publish again.')


def acknowledge(item):
    item['entry']['original'] = item['text']
    save_json(item['directory'] / STATE, item['state'])
    (item['directory'] / (item['entry']['file'] + '.live')).unlink(missing_ok=True)


def rebase(args):
    """Move each baseline to the current GitHub text, keeping local edits.

    Unedited files take the current text. An edited file whose remote text changed keeps the edit; the current
    text is saved beside it as <file>.live for the agent to merge before publishing again.
    """
    for directory in dict.fromkeys(Path(value).expanduser().resolve() for value in args.directories):
        state = load(directory)
        items = [{'directory': directory, 'state': state, 'entry': entry,
                  'text': (directory / entry['file']).read_text()} for entry in state['entries']]
        with ThreadPoolExecutor(max_workers=6) as pool:
            live = list(pool.map(current, items))
        merges = 0
        for item, text in zip(items, live):
            entry, path = item['entry'], directory / item['entry']['file']
            if text == entry['original']:
                continue
            if item['text'] == entry['original']:
                path.write_text(text)
                entry['original'] = text
            elif item['text'] == text:
                entry['original'] = text
            else:
                (directory / (entry['file'] + '.live')).write_text(text)
                entry['original'] = text
                merges += 1
                print(f'Merge needed: {path} (current GitHub text in {path}.live; delete it once merged)')
        save_json(directory / STATE, state)
        print(f"{state['repo']}#{state['number']}: baseline moved to current GitHub text, {merges} file(s) to merge")


def publish(args):
    changes = collect(args.directories)
    if not changes:
        print('No pending edits.')
        return
    unmerged = [item['directory'] / (item['entry']['file'] + '.live') for item in changes
                if (item['directory'] / (item['entry']['file'] + '.live')).exists()]
    if unmerged:
        raise RuntimeError('Merge these into their edited files and delete them before publishing: '
                           + ', '.join(str(path) for path in unmerged))
    with ThreadPoolExecutor(max_workers=6) as pool:
        live = list(pool.map(current, changes))
    for item, text in zip(changes, live):
        check(item, text)

    completed = 0
    try:
        for item in changes:
            # Recheck immediately before each write. GitHub does not provide a multi-comment transaction.
            text = current(item)
            check(item, text)
            if text != item['text']:
                raw = item['directory'] / '.responses'
                payload = raw / (item['entry']['file'] + '.payload.json')
                save_json(payload, {'body': item['text']})
                api(endpoint(item['state'], item['entry']), raw / 'patch.json', 'PATCH', payload)
                if current(item) != item['text']:
                    raise RuntimeError(f"Read-back mismatch: {item['directory'] / item['entry']['file']}")
            # A previous interrupted attempt may already have published this exact text.
            acknowledge(item)
            completed += 1
            print(f"Verified {item['state']['repo']}#{item['state']['number']}: {item['entry']['file']}", flush=True)
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f'Stopped after {completed} verified updates; no rollback was attempted. {error}') from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('fetch', help='Fetch issue bodies/comments into per-session editing directories.')
    command.add_argument('references', nargs='+', metavar='OWNER/REPO#NUMBER')
    command.add_argument('--session', help='Override the agent session ID used in temporary directory names.')
    for name, description in [('status', 'List edited files without their contents.'),
                              ('preview', 'Show pending Markdown diffs.'),
                              ('publish', 'Check for concurrent changes, upload edited bodies, and verify them.'),
                              ('rebase', 'After a concurrent edit, move the baseline to the current GitHub text, '
                                         'keeping local edits.')]:
        command = commands.add_parser(name, help=description)
        command.add_argument('directories', nargs='+', metavar='DIRECTORY')
    args = parser.parse_args()
    try:
        if args.command == 'fetch':
            fetch(args)
        elif args.command == 'publish':
            publish(args)
        elif args.command == 'rebase':
            rebase(args)
        else:
            report(args)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f'plan_comments: {error}\n')


if __name__ == '__main__':
    main()
