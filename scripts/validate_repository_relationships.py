#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(ROOT / 'scripts'))

from repository_relationships_lib import (  # noqa: E402
    PUBLIC_AUDIENCE,
    RelationshipValidationError,
    parse_manual_declarations,
    validate_relationship_graph,
)


def fail(message: str) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)

required = [
    'repository-relationships.json',
    'repository-relationships.manual.json',
    'repository-relationships.schema.json',
    'repository-relationships.manual.schema.json',
    'docs/REPOSITORY_RELATIONSHIPS.md',
]
missing = [path for path in required if not (ROOT / path).is_file()]
if missing:
    fail('missing relationship files: ' + ', '.join(missing))

try:
    graph = json.loads((ROOT / 'repository-relationships.json').read_text(encoding='utf-8'))
    validate_relationship_graph(graph)
    owner = graph['owner']['login']
    parse_manual_declarations(
        (ROOT / 'repository-relationships.manual.json').read_text(encoding='utf-8'),
        owner,
        audience=PUBLIC_AUDIENCE,
    )
    for schema_path in (
        ROOT / 'repository-relationships.schema.json',
        ROOT / 'repository-relationships.manual.schema.json',
    ):
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
        if schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema':
            fail(f'{schema_path.name} is not JSON Schema draft 2020-12')
except (KeyError, json.JSONDecodeError, RelationshipValidationError) as exc:
    fail(str(exc))

markdown = (ROOT / 'docs/REPOSITORY_RELATIONSHIPS.md').read_text(encoding='utf-8')
if graph['generated']['inventory_digest'] not in markdown:
    fail('relationship documentation digest does not match JSON registry')
if graph.get('audience') != PUBLIC_AUDIENCE:
    fail('organization .github relationship registry must have public audience')

print(
    'PASS: validated repository relationship registry for '
    f"{owner} ({len(graph['repositories'])} repositories, {len(graph['relationships'])} relationships)"
)
