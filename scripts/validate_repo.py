#!/usr/bin/env python3
"""Validate portable skill structure, local links and common secret markers.

Heuristic scan only; public release also needs human content review.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'private-key': r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----',
    'api-token': r'\bsk-[A-Za-z0-9_-]{16,}',
    'github-token': r'\b(?:ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}',
    'cloud-access-id': r'\bAKID[A-Za-z0-9]{16,}',
    'ipv4-address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'email-address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'media-xml-secret': r'<(?:aeskey|newformataeskey)>',
}

def check(root):
    errors = []
    skills = sorted((root / 'skills').glob('*/SKILL.md'))
    if not skills:
        errors.append(('skills', 'no skills found'))
    for p in skills:
        text = p.read_text()
        match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        meta = dict(re.findall(r'^(name|description):\s*(.+)$', match[1], re.M)) if match else {}
        if meta.get('name') != p.parent.name or not re.fullmatch(r'[a-z0-9-]{1,63}', meta.get('name', '')):
            errors.append((str(p.relative_to(root)), 'invalid skill name or frontmatter'))
        if not meta.get('description'):
            errors.append((str(p.relative_to(root)), 'missing description'))
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(part in {'.git', '__pycache__'} for part in p.relative_to(root).parts):
            continue
        if p.suffix not in {'.md', '.json', '.yml', '.yaml'}:
            continue
        text = p.read_text()
        rel = str(p.relative_to(root))
        if p.name == 'APIONE正式上线群.md':
            errors.append((rel, 'raw chat forbidden'))
        for name, pattern in PATTERNS.items():
            if re.search(pattern, text):
                errors.append((rel, name))
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if re.match(r'[a-z]+://', target) or target.startswith('#'):
                    continue
                path = target.split('#')[0]
                if path and not (p.parent / path).exists():
                    errors.append((rel, 'broken local link'))
    return skills, errors

if __name__ == '__main__':
    skills, errors = check(ROOT)
    for path, reason in errors:
        print(f'{path}: {reason}')  # Never print matching secret values.
    if errors:
        sys.exit(1)
    print(f'PASS: {len(skills)} skills; frontmatter, local links and heuristic public-content scan')
