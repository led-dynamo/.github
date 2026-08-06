#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
REQUIRED = [
    'README.md', 'profile/README.md', 'ORG_CONTEXT.md', 'agents.md', 'AGENTS.md',
    'CONTRIBUTING.md', 'SECURITY.md', 'SUPPORT.md', 'CODE_OF_CONDUCT.md',
    'GOVERNANCE.md', '.github/pull_request_template.md',
    '.github/copilot-instructions.md', '.github/dependabot.yml',
    '.github/ISSUE_TEMPLATE/bug_report.yml',
    '.github/ISSUE_TEMPLATE/feature_request.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/workflows/baseline-policy.yml',
    '.github/workflows/reusable-policy.yml',
    '.github/workflows/repository-relationships.yml',
    'repository-relationships.json',
    'repository-relationships.manual.json',
    'repository-relationships.schema.json',
    'repository-relationships.manual.schema.json',
    'docs/REPOSITORY_RELATIONSHIPS.md',
    'scripts/repository_relationships_lib.py',
    'scripts/validate_repository_relationships.py',
]
PHRASES = [
    'avoid git rebase in favor of git merge',
    'git stash', 'git reset', 'git clean', 'git filter-repo',
    '3–10 relevant commits', 'Never report',
]
SECRET_PATTERNS = [
    re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?i)authorization:\\s*bearer\\s+[A-Za-z0-9._-]{16,}'),
]

def fail(message: str) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)

missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
if missing:
    fail('missing required files: ' + ', '.join(missing))

agents = (ROOT / 'agents.md').read_text(encoding='utf-8')
for phrase in PHRASES:
    if phrase not in agents:
        fail(f'agents.md missing required phrase: {phrase!r}')

for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts:
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    if re.search(r'\{\{[A-Z][A-Z0-9_]*\}\}', text):
        fail(f'unrendered placeholder in {path.relative_to(ROOT)}')
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            fail(f'possible credential in {path.relative_to(ROOT)}')
    if text and not text.endswith('\n'):
        fail(f'missing final newline: {path.relative_to(ROOT)}')

workflow_paths = list((ROOT / '.github/workflows').glob('*.y*ml'))
workflow_paths += list((ROOT / 'workflow-templates').glob('*.y*ml'))
for path in workflow_paths:
    text = path.read_text(encoding='utf-8')
    if 'permissions:' not in text:
        fail(f'workflow lacks explicit permissions: {path.relative_to(ROOT)}')
    if 'timeout-minutes:' not in text:
        fail(f'workflow lacks timeout: {path.relative_to(ROOT)}')
    for number, line in enumerate(text.splitlines(), 1):
        match = re.search(r'^\\s*(?:-\\s+)?uses:\\s*([^\\s#]+)', line)
        if not match:
            continue
        ref = match.group(1)
        if ref.startswith('./'):
            continue
        if ref.startswith('docker://'):
            if not re.search(r'@sha256:[0-9a-fA-F]{64}$', ref):
                fail(f'external Docker action is not digest-pinned: {path.relative_to(ROOT)}:{number}: {ref}')
            continue
        if not re.search(r'@[0-9a-fA-F]{40}$', ref):
            fail(f'external Action is not pinned to a full SHA: {path.relative_to(ROOT)}:{number}: {ref}')
    if 'actions/checkout@' in text and 'persist-credentials: false' not in text:
        fail(f'checkout credentials persist in {path.relative_to(ROOT)}')

import subprocess
relationship_check = subprocess.run(
    [sys.executable, str(ROOT / 'scripts/validate_repository_relationships.py'), str(ROOT)],
    text=True, capture_output=True, check=False,
)
if relationship_check.returncode != 0:
    fail('relationship registry validation failed: ' + (relationship_check.stderr or relationship_check.stdout).strip())

print(f'PASS: validated {ROOT}')
