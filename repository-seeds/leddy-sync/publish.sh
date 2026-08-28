#!/usr/bin/env bash
set -euo pipefail

repository="led-dynamo/leddy-sync"
description="Deterministic synchronization primitives for the Leddy fleet"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
temp_dir="$(mktemp -d)"
askpass="$temp_dir/git-askpass.sh"
trap 'rm -rf "$temp_dir"' EXIT

github_host="${GITHUB_HOST:-github.com}"
api_url="${GITHUB_API_URL:-https://api.github.com}"
github_token="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
use_gh=false

command -v git >/dev/null 2>&1 || {
  echo "git is required" >&2
  exit 127
}

if command -v gh >/dev/null 2>&1 && gh auth status --hostname "$github_host" >/dev/null 2>&1; then
  use_gh=true
else
  command -v python3 >/dev/null 2>&1 || {
    echo "Authenticated gh or Python 3 with GH_TOKEN is required" >&2
    exit 127
  }
  if [[ -z "$github_token" ]]; then
    echo "Authenticate gh, or set GH_TOKEN (GITHUB_TOKEN is also accepted)" >&2
    exit 126
  fi
fi

api_request() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  GITHUB_REQUEST_METHOD="$method" \
  GITHUB_REQUEST_PATH="$path" \
  GITHUB_REQUEST_BODY="$body" \
  GITHUB_API_URL="$api_url" \
  GH_TOKEN="$github_token" \
  python3 -S - <<'PY'
import os
import sys
import urllib.error
import urllib.request

method = os.environ["GITHUB_REQUEST_METHOD"]
path = os.environ["GITHUB_REQUEST_PATH"]
body = os.environ.get("GITHUB_REQUEST_BODY", "")
base = os.environ["GITHUB_API_URL"].rstrip("/")
token = os.environ["GH_TOKEN"]
data = body.encode("utf-8") if body else None
request = urllib.request.Request(
    f"{base}{path}",
    data=data,
    method=method,
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "led-dynamo-repository-publisher",
    },
)
try:
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8", errors="replace")
        print(response.status)
        if response_body:
            print(response_body)
except urllib.error.HTTPError as error:
    response_body = error.read().decode("utf-8", errors="replace")
    print(error.code)
    if response_body:
        print(response_body)
except urllib.error.URLError as error:
    print(f"NETWORK_ERROR:{error.reason}", file=sys.stderr)
    raise SystemExit(2)
PY
}

repo_exists() {
  local target="$1"
  if [[ "$use_gh" == true ]]; then
    gh repo view "$target" >/dev/null 2>&1
    return
  fi

  local output status
  output="$(api_request GET "/repos/$target")" || return 2
  status="${output%%$'\n'*}"
  case "$status" in
    200) return 0 ;;
    404) return 1 ;;
    *)
      echo "GitHub repository lookup failed for $target (HTTP $status)" >&2
      printf '%s\n' "${output#*$'\n'}" >&2
      return 2
      ;;
  esac
}

if repo_exists "$repository"; then
  echo "$repository already exists; refusing to overwrite it" >&2
  exit 17
else
  lookup_status=$?
  if [[ "$lookup_status" -ne 1 ]]; then
    exit "$lookup_status"
  fi
fi

if ! git -C "$repo_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$repo_dir" init --initial-branch=main
  git -C "$repo_dir" config user.name "ORESoftware automation"
  git -C "$repo_dir" config user.email "11139560+ORESoftware@users.noreply.github.com"
  git -C "$repo_dir" add --all
  git -C "$repo_dir" commit -m "bootstrap canonical Leddy sync package"
fi

if [[ -n "$(git -C "$repo_dir" status --porcelain)" ]]; then
  echo "Refusing to publish a dirty working tree: $repo_dir" >&2
  exit 21
fi

current_branch="$(git -C "$repo_dir" branch --show-current)"
if [[ "$current_branch" != "main" ]]; then
  echo "Refusing to publish branch '$current_branch'; expected main" >&2
  exit 22
fi

if git -C "$repo_dir" remote get-url origin >/dev/null 2>&1; then
  origin_url="$(git -C "$repo_dir" remote get-url origin)"
  case "$origin_url" in
    "https://$github_host/$repository.git"|"git@$github_host:$repository.git") ;;
    *)
      echo "Refusing to replace unrelated origin remote: $origin_url" >&2
      exit 23
      ;;
  esac
fi

if [[ "$use_gh" == true ]]; then
  gh_args=(
    repo create "$repository"
    --public
    --description "$description"
    --source "$repo_dir"
    --push
  )
  if ! git -C "$repo_dir" remote get-url origin >/dev/null 2>&1; then
    gh_args+=(--remote origin)
  fi
  gh "${gh_args[@]}"
else
  owner="${repository%%/*}"
  name="${repository#*/}"
  payload="$(python3 -S - "$name" "$description" <<'PY'
import json
import sys
print(json.dumps({
    "name": sys.argv[1],
    "description": sys.argv[2],
    "private": False,
    "auto_init": False,
}))
PY
)"
  output="$(api_request POST "/orgs/$owner/repos" "$payload")" || {
    echo "GitHub repository creation request failed" >&2
    exit 20
  }
  status="${output%%$'\n'*}"
  if [[ "$status" != "201" ]]; then
    echo "GitHub repository creation failed for $repository (HTTP $status)" >&2
    printf '%s\n' "${output#*$'\n'}" >&2
    exit 20
  fi

  if ! git -C "$repo_dir" remote get-url origin >/dev/null 2>&1; then
    git -C "$repo_dir" remote add origin "https://$github_host/$repository.git"
  fi

  cat >"$askpass" <<'EOF'
#!/usr/bin/env sh
case "$1" in
  *Username*) printf '%s\n' "x-access-token" ;;
  *Password*) printf '%s\n' "${GH_TOKEN:?GH_TOKEN is required}" ;;
  *) exit 1 ;;
esac
EOF
  chmod 700 "$askpass"

  GH_TOKEN="$github_token" GIT_TERMINAL_PROMPT=0 \
    git -C "$repo_dir" \
      -c credential.helper= \
      -c core.askPass="$askpass" \
      push --set-upstream origin main
fi

echo "published https://$github_host/$repository"
