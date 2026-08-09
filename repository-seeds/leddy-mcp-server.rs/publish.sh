#!/usr/bin/env bash
set -euo pipefail

repository="led-dynamo/leddy-mcp-server.rs"
seed_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work_dir="$(mktemp -d)"
trap 'printf "temporary publication workspace retained at %s\n" "$work_dir" >&2' ERR
trap 'if [[ -d "$work_dir" ]]; then printf "temporary publication workspace: %s\n" "$work_dir" >&2; fi' EXIT

for command in gh git cargo python3 tar; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "$command is required" >&2
    exit 127
  }
done

gh auth status --hostname github.com >/dev/null

gh repo view "led-dynamo/leddy-sync" >/dev/null 2>&1 || {
  echo "led-dynamo/leddy-sync must be published and validated first" >&2
  exit 18
}

if gh repo view "$repository" >/dev/null 2>&1; then
  echo "$repository already exists; refusing to overwrite it" >&2
  exit 17
fi

# Copy the reviewed seed without its local publisher. No source file is removed or rewritten.
tar --exclude='./publish.sh' -C "$seed_dir" -cf - . | tar -C "$work_dir" -xf -

cargo generate-lockfile --manifest-path "$work_dir/Cargo.toml"

SEED_WORK_DIR="$work_dir" python3 - <<'PY'
import hashlib
import json
import os
import pathlib
import tomllib

root = pathlib.Path(os.environ['SEED_WORK_DIR'])
manifest = tomllib.loads((root / 'Cargo.toml').read_text(encoding='utf-8'))
if manifest['dependencies']['rmcp']['version'] != '=3.1.0':
    raise SystemExit('rmcp must be pinned exactly to =3.1.0')
lock = tomllib.loads((root / 'Cargo.lock').read_text(encoding='utf-8'))
versions = {
    package['name']: package['version']
    for package in lock['package']
    if package['name'] in {'rmcp', 'rmcp-macros'}
}
if versions != {'rmcp': '3.1.0', 'rmcp-macros': '3.1.0'}:
    raise SystemExit(f'unexpected official SDK resolution: {versions!r}')

api_manifest = json.loads((root / 'openapi/api-docs.manifest.json').read_text(encoding='utf-8'))
openapi_bytes = (root / 'openapi/leddy.openapi.json').read_bytes()
digest = hashlib.sha256(openapi_bytes).hexdigest()
if digest != 'cf0be66ce0ebb02c3fc077a88c3129c55b4d05f30070b3c7186d13731ae7fe88':
    raise SystemExit(f'unexpected OpenAPI digest: {digest}')
if api_manifest['public']['openapi']['sha256'] != digest:
    raise SystemExit('manifest and OpenAPI digest disagree')
PY

cargo fmt --manifest-path "$work_dir/Cargo.toml" --all -- --check
cargo clippy --manifest-path "$work_dir/Cargo.toml" --locked --all-targets --all-features -- -D warnings
cargo test --manifest-path "$work_dir/Cargo.toml" --locked --all-targets --all-features
RUSTDOCFLAGS='-D warnings' cargo doc --manifest-path "$work_dir/Cargo.toml" --locked --no-deps
cargo build --manifest-path "$work_dir/Cargo.toml" --locked --release

git -C "$work_dir" init --initial-branch=main
git -C "$work_dir" config user.name "ORESoftware automation"
git -C "$work_dir" config user.email "11139560+ORESoftware@users.noreply.github.com"
git -C "$work_dir" add --all
git -C "$work_dir" commit -m "bootstrap canonical Leddy API-docs MCP server"

gh repo create "$repository" \
  --public \
  --description "Read-only official-rmcp server for canonical Leddy API documentation" \
  --source "$work_dir" \
  --remote origin \
  --push

gh repo edit "$repository" \
  --enable-issues \
  --enable-discussions=false \
  --enable-wiki=false \
  --add-topic api-docs \
  --add-topic led-matrix \
  --add-topic mcp \
  --add-topic rust \
  --add-topic zed-package

printf 'published https://github.com/%s\n' "$repository"
