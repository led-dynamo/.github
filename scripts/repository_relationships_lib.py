#!/usr/bin/env python3
"""Deterministic, privacy-aware repository relationship graph construction.

The public graph is safe for an organization's public ``.github`` repository:
private repositories and relationships that would reveal them are omitted.  A
complete graph may be synchronized to the private ``approved-private-registry``
repository by the rollout client.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = 1
MANAGED_BY = "ore-repository-relationship-rollout"
GENERATOR_VERSION = "2026-08-04.1"
PUBLIC_AUDIENCE = "public"
PRIVATE_AUDIENCE = "private"

ALLOWED_RELATIONSHIP_TYPES = {
    "governs",
    "documents",
    "tests",
    "deploys",
    "depends_on",
    "implements",
    "publishes",
    "mirrors",
    "contains",
    "shares_contract_with",
    "uses_workflow_from",
    "submodule_of",
    "integrates_with",
    "supersedes",
}
ALLOWED_STATUSES = {"declared", "observed", "inferred", "proposed"}
ALLOWED_SCOPES = {"organization", "cross-organization"}
STATUS_PRIORITY = {"proposed": 0, "inferred": 1, "observed": 2, "declared": 3}

LANGUAGE_SUFFIXES = (
    ".rs", ".go", ".ts", ".js", ".dart", ".gleam", ".ex", ".exs", ".erl", ".py",
)
ROLE_SUFFIXES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("end-to-end-tests", ("-e2e", "-end-to-end", "-integration-tests")),
    ("tests", ("-tests", "-test")),
    ("infrastructure", ("-infra", "-infrastructure")),
    ("clients", ("-clients", "-client")),
    ("interfaces", ("-interfaces", "-interface", "-contracts", "-contract")),
    ("mcp-server", ("-mcp-server",)),
    ("api-server", ("-api-server", "-api")),
    ("web-server", ("-web-server",)),
    ("backend", ("-backend",)),
    ("sync", ("-sync",)),
    ("monorepo", ("-monorepo",)),
    ("sdk", ("-sdks", "-sdk")),
)

SECRET_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._-]{16,}"),
)


class RelationshipValidationError(ValueError):
    """Raised when a relationship graph or manual declaration is invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_prefixed(value: Any) -> str:
    payload = value if isinstance(value, str) else canonical_json(value)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def without_language_suffix(name: str) -> str:
    lowered = name.casefold()
    for suffix in sorted(LANGUAGE_SUFFIXES, key=len, reverse=True):
        if lowered.endswith(suffix):
            return name[: -len(suffix)]
    return name


def repository_role(name: str) -> tuple[str, str]:
    """Return a conservative role and family stem derived from a repository name."""
    base = without_language_suffix(name).casefold()
    if base == ".github":
        return "governance", base
    if base.endswith(".github.io"):
        return "documentation-site", base[: -len(".github.io")]
    for role, suffixes in ROLE_SUFFIXES:
        for suffix in sorted(suffixes, key=len, reverse=True):
            if base.endswith(suffix) and len(base) > len(suffix):
                return role, base[: -len(suffix)]
    return "repository", base


def repository_roles(name: str) -> list[str]:
    role, _ = repository_role(name)
    roles = [role]
    if name == ".github":
        roles.extend(["community-health", "relationship-registry"])
    return sorted(set(roles))


def normalize_repository(raw: Mapping[str, Any], owner: str, *, synthetic: bool = False) -> dict[str, Any]:
    name = str(raw.get("name") or "").strip()
    if not name:
        raise RelationshipValidationError("repository record is missing name")
    full_name = str(raw.get("full_name") or f"{owner}/{name}").strip()
    visibility = str(raw.get("visibility") or ("private" if raw.get("private") else "public"))
    if visibility not in {"public", "private", "internal"}:
        raise RelationshipValidationError(f"unsupported visibility for {full_name}: {visibility}")
    record = {
        "name": name,
        "full_name": full_name,
        "owner": full_name.split("/", 1)[0] if "/" in full_name else owner,
        "visibility": visibility,
        "default_branch": raw.get("default_branch") or "main",
        "archived": bool(raw.get("archived", False)),
        "fork": bool(raw.get("fork", False)),
        "roles": repository_roles(name),
        "source": "synthetic-bootstrap" if synthetic else "github-rest-api",
    }
    if raw.get("html_url"):
        record["url"] = raw["html_url"]
    if raw.get("id") is not None:
        record["github_id"] = str(raw["id"])
    return record


def _edge_identity(edge: Mapping[str, Any]) -> str:
    return "\n".join(
        [str(edge.get("from", "")), str(edge.get("type", "")), str(edge.get("to", ""))]
    )


def relationship_id(edge: Mapping[str, Any]) -> str:
    return sha256_prefixed(_edge_identity(edge))


def make_relationship(
    source: str,
    target: str,
    relationship_type: str,
    *,
    status: str,
    scope: str,
    required: bool = False,
    confidence: float | None = None,
    evidence: Sequence[Mapping[str, Any]] | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    edge: dict[str, Any] = {
        "from": source,
        "to": target,
        "type": relationship_type,
        "status": status,
        "scope": scope,
        "required": bool(required),
        "evidence": [dict(item) for item in (evidence or [])],
    }
    edge["id"] = relationship_id(edge)
    if confidence is not None:
        edge["confidence"] = round(float(confidence), 3)
    if notes:
        edge["notes"] = notes
    return edge


def _preferred_edge(current: Mapping[str, Any], proposed: Mapping[str, Any]) -> dict[str, Any]:
    current_priority = STATUS_PRIORITY.get(str(current.get("status")), -1)
    proposed_priority = STATUS_PRIORITY.get(str(proposed.get("status")), -1)
    if proposed_priority > current_priority:
        return dict(proposed)
    if proposed_priority < current_priority:
        return dict(current)
    current_evidence = len(current.get("evidence") or [])
    proposed_evidence = len(proposed.get("evidence") or [])
    return dict(proposed if proposed_evidence > current_evidence else current)


def deduplicate_relationships(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for raw in edges:
        edge = dict(raw)
        edge["id"] = relationship_id(edge)
        key = (str(edge.get("from")), str(edge.get("type")), str(edge.get("to")))
        if key in chosen:
            chosen[key] = _preferred_edge(chosen[key], edge)
        else:
            chosen[key] = edge
    return sorted(chosen.values(), key=lambda item: (item["from"].casefold(), item["type"], item["to"].casefold()))


def empty_manual_declarations(owner: str) -> dict[str, Any]:
    return {
        "$schema": "./repository-relationships.manual.schema.json",
        "schema_version": SCHEMA_VERSION,
        "owner": owner,
        "repositories": [],
        "relationships": [],
        "notes": [
            "Declare reviewed repository relationships here; generated inventory belongs in repository-relationships.json.",
            "A public .github repository must not name private repositories. Put private declarations in approved-private-registry.",
        ],
    }


def parse_manual_declarations(text: str | None, owner: str, *, audience: str) -> dict[str, Any]:
    if not text:
        return empty_manual_declarations(owner)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RelationshipValidationError(f"invalid repository-relationships.manual.json: {exc}") from exc
    if not isinstance(payload, dict):
        raise RelationshipValidationError("manual relationship declaration must be a JSON object")
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if str(payload.get("owner", "")).casefold() != owner.casefold():
        errors.append(f"manual owner must equal {owner}")
    repositories = payload.get("repositories", [])
    relationships = payload.get("relationships", [])
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    if not isinstance(relationships, list):
        errors.append("relationships must be an array")
        relationships = []
    for index, repo in enumerate(repositories):
        if not isinstance(repo, dict) or not repo.get("full_name"):
            errors.append(f"repositories[{index}] must contain full_name")
            continue
        visibility = repo.get("visibility", "public")
        if audience == PUBLIC_AUDIENCE and visibility != "public":
            errors.append(f"repositories[{index}] exposes non-public repository {repo.get('full_name')}")
    for index, edge in enumerate(relationships):
        if not isinstance(edge, dict):
            errors.append(f"relationships[{index}] must be an object")
            continue
        for field in ("from", "to", "type"):
            if not edge.get(field):
                errors.append(f"relationships[{index}] is missing {field}")
        if edge.get("type") not in ALLOWED_RELATIONSHIP_TYPES:
            errors.append(f"relationships[{index}] has unsupported type {edge.get('type')!r}")
        if edge.get("status", "declared") not in ALLOWED_STATUSES:
            errors.append(f"relationships[{index}] has unsupported status")
    if errors:
        raise RelationshipValidationError("; ".join(errors))
    return payload


def _manual_repository_record(raw: Mapping[str, Any], owner: str) -> dict[str, Any]:
    full_name = str(raw["full_name"])
    name = full_name.split("/", 1)[1] if "/" in full_name else full_name
    visibility = str(raw.get("visibility", "public"))
    record = normalize_repository(
        {
            "name": name,
            "full_name": full_name,
            "visibility": visibility,
            "default_branch": raw.get("default_branch", "main"),
            "archived": raw.get("archived", False),
            "fork": raw.get("fork", False),
            "html_url": raw.get("url"),
        },
        owner,
    )
    record["source"] = "manual-declaration"
    record["external"] = record["owner"].casefold() != owner.casefold()
    return record


def infer_relationships(repositories: Sequence[Mapping[str, Any]], owner: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Infer only conservative naming-convention edges.

    Inferences are explicitly labeled and never replace a reviewed declaration.
    Ambiguous matches are emitted as hints rather than guessed edges.
    """
    by_role: dict[str, list[Mapping[str, Any]]] = {}
    details: dict[str, tuple[str, str]] = {}
    for repo in repositories:
        role, family = repository_role(str(repo["name"]))
        by_role.setdefault(role, []).append(repo)
        details[str(repo["full_name"])] = (role, family)

    edges: list[dict[str, Any]] = []
    hints: list[dict[str, Any]] = []
    dotgithub = next((repo for repo in repositories if repo["name"] == ".github" and repo["owner"].casefold() == owner.casefold()), None)
    if dotgithub:
        for repo in repositories:
            if repo["full_name"] == dotgithub["full_name"] or repo["owner"].casefold() != owner.casefold():
                continue
            edges.append(make_relationship(
                str(dotgithub["full_name"]), str(repo["full_name"]), "governs",
                status="declared", scope="organization", required=True, confidence=1.0,
                evidence=[{
                    "kind": "github-owner-membership",
                    "source": "GitHub REST repository inventory",
                }],
                notes="Organization .github policy and community-health defaults govern this sibling repository.",
            ))

    for repo in repositories:
        full_name = str(repo["full_name"])
        role, family = details[full_name]
        if repo["owner"].casefold() != owner.casefold():
            continue
        if role == "documentation-site" and dotgithub:
            edges.append(make_relationship(
                full_name, str(dotgithub["full_name"]), "documents",
                status="inferred", scope="organization", confidence=0.95,
                evidence=[{"kind": "repository-name", "value": repo["name"]}],
                notes="The conventional *.github.io repository documents the organization profile.",
            ))

        if role in {"clients", "mcp-server", "api-server", "web-server", "backend", "sync"}:
            interfaces = [
                candidate for candidate in by_role.get("interfaces", [])
                if details[str(candidate["full_name"])][1] == family
            ]
            if len(interfaces) == 1:
                edges.append(make_relationship(
                    full_name, str(interfaces[0]["full_name"]), "depends_on",
                    status="inferred", scope="organization", confidence=0.82,
                    evidence=[{
                        "kind": "paired-repository-naming",
                        "source_role": role,
                        "target_role": "interfaces",
                        "family": family,
                    }],
                    notes="Conservative naming inference; confirm or override in the manual declaration file.",
                ))
            elif len(interfaces) > 1:
                hints.append({
                    "source": full_name,
                    "proposed_type": "depends_on",
                    "reason": "multiple interface repositories share the same naming family",
                    "candidates": sorted(str(item["full_name"]) for item in interfaces),
                })

        if role in {"end-to-end-tests", "tests"}:
            candidates = [
                candidate for candidate in by_role.get("monorepo", [])
                if details[str(candidate["full_name"])][1] == family
            ]
            if not candidates:
                candidates = [
                    candidate for candidate in repositories
                    if candidate["owner"].casefold() == owner.casefold()
                    and candidate["full_name"] != full_name
                    and details[str(candidate["full_name"])][1] == family
                    and details[str(candidate["full_name"])][0] in {"repository", "api-server", "web-server", "backend"}
                ]
            if len(candidates) == 1:
                edges.append(make_relationship(
                    full_name, str(candidates[0]["full_name"]), "tests",
                    status="inferred", scope="organization", confidence=0.78,
                    evidence=[{"kind": "paired-repository-naming", "family": family}],
                    notes="Conservative naming inference; confirm or override in the manual declaration file.",
                ))
            elif len(candidates) > 1:
                hints.append({
                    "source": full_name,
                    "proposed_type": "tests",
                    "reason": "test target is ambiguous",
                    "candidates": sorted(str(item["full_name"]) for item in candidates),
                })

        if role == "infrastructure":
            candidates = [
                candidate for candidate in by_role.get("monorepo", [])
                if details[str(candidate["full_name"])][1] == family
            ]
            if len(candidates) == 1:
                edges.append(make_relationship(
                    full_name, str(candidates[0]["full_name"]), "deploys",
                    status="inferred", scope="organization", confidence=0.76,
                    evidence=[{"kind": "paired-repository-naming", "family": family}],
                    notes="Conservative naming inference; confirm or override in the manual declaration file.",
                ))
            elif len(candidates) > 1:
                hints.append({
                    "source": full_name,
                    "proposed_type": "deploys",
                    "reason": "deployment target is ambiguous",
                    "candidates": sorted(str(item["full_name"]) for item in candidates),
                })

    return deduplicate_relationships(edges), sorted(hints, key=lambda item: (item["source"].casefold(), item["proposed_type"]))


def _manual_edges(manual: Mapping[str, Any], owner: str) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for raw in manual.get("relationships", []):
        source = str(raw["from"])
        target = str(raw["to"])
        scope = raw.get("scope") or (
            "organization"
            if source.split("/", 1)[0].casefold() == owner.casefold()
            and target.split("/", 1)[0].casefold() == owner.casefold()
            else "cross-organization"
        )
        evidence = list(raw.get("evidence") or [])
        if not evidence:
            evidence = [{"kind": "manual-review", "source": "repository-relationships.manual.json"}]
        edges.append(make_relationship(
            source,
            target,
            str(raw["type"]),
            status=str(raw.get("status", "declared")),
            scope=str(scope),
            required=bool(raw.get("required", False)),
            confidence=float(raw.get("confidence", 1.0)),
            evidence=evidence,
            notes=raw.get("notes"),
        ))
    return edges


def build_relationship_graph(
    target: Mapping[str, Any],
    api_repositories: Sequence[Mapping[str, Any]],
    *,
    audience: str,
    manual: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
    private_graph_digest: str | None = None,
) -> dict[str, Any]:
    if audience not in {PUBLIC_AUDIENCE, PRIVATE_AUDIENCE}:
        raise ValueError(f"unsupported audience: {audience}")
    owner = str(target["owner"])
    manual_payload = dict(manual or empty_manual_declarations(owner))
    if audience == PUBLIC_AUDIENCE and not private_graph_digest:
        private_graph = build_relationship_graph(
            target,
            api_repositories,
            audience=PRIVATE_AUDIENCE,
            manual=manual_payload,
            generated_at=generated_at,
        )
        private_graph_digest = str(private_graph["generated"]["inventory_digest"])

    normalized: dict[str, dict[str, Any]] = {}
    omitted_nonpublic: set[str] = set()
    for raw in api_repositories:
        record = normalize_repository(raw, owner)
        if audience == PUBLIC_AUDIENCE and record["visibility"] != "public":
            omitted_nonpublic.add(record["full_name"].casefold())
            continue
        normalized[record["full_name"].casefold()] = record

    dotgithub_key = f"{owner}/.github".casefold()
    if dotgithub_key not in normalized:
        normalized[dotgithub_key] = normalize_repository(
            {
                "name": ".github",
                "full_name": f"{owner}/.github",
                "visibility": "public",
                "default_branch": "main",
                "archived": False,
            },
            owner,
            synthetic=True,
        )

    for raw in manual_payload.get("repositories", []):
        record = _manual_repository_record(raw, owner)
        if audience == PUBLIC_AUDIENCE and record["visibility"] != "public":
            omitted_nonpublic.add(record["full_name"].casefold())
            continue
        normalized.setdefault(record["full_name"].casefold(), record)

    repositories = sorted(normalized.values(), key=lambda item: item["full_name"].casefold())
    inferred, hints = infer_relationships(repositories, owner)
    relationships = deduplicate_relationships([*inferred, *_manual_edges(manual_payload, owner)])

    digest_payload = {
        "schema_version": SCHEMA_VERSION,
        "owner": owner,
        "audience": audience,
        "repositories": repositories,
        "relationships": relationships,
        "unresolved_hints": hints,
    }
    digest = sha256_prefixed(digest_payload)
    graph: dict[str, Any] = {
        "$schema": "./repository-relationships.schema.json",
        "schema_version": SCHEMA_VERSION,
        "owner": {
            "login": owner,
            "account_type": target.get("account_type", "organization"),
            "dotgithub_repository": f"{owner}/.github",
            "linear_project": {
                "name": target.get("linear_project"),
                "url": target.get("linear_url"),
            },
        },
        "audience": audience,
        "generated": {
            "managed_by": MANAGED_BY,
            "generator_version": GENERATOR_VERSION,
            "generated_at": generated_at or utc_now(),
            "source": "GitHub REST repository inventory plus reviewed manual declarations",
            "inventory_digest": digest,
            "complete_for_visibility": "public" if audience == PUBLIC_AUDIENCE else "accessible-to-rollout-credential",
            "private_repositories_omitted": bool(omitted_nonpublic) if audience == PUBLIC_AUDIENCE else False,
            "omitted_repository_count": len(omitted_nonpublic) if audience == PUBLIC_AUDIENCE else 0,
        },
        "repositories": repositories,
        "relationships": relationships,
        "unresolved_hints": hints,
    }
    if audience == PUBLIC_AUDIENCE:
        graph["private_registry"] = {
            "repository": "approved-private-registry",
            "path": f"owners/{owner}.json",
            "contains_non_public_inventory": bool(omitted_nonpublic),
            "digest": private_graph_digest,
        }
    validate_relationship_graph(graph)
    return graph


def stabilize_generated_at(graph: dict[str, Any], existing_text: str | None) -> dict[str, Any]:
    """Avoid timestamp-only churn when the relationship digest is unchanged."""
    if not existing_text:
        return graph
    try:
        existing = json.loads(existing_text)
    except json.JSONDecodeError:
        return graph
    old_generated = existing.get("generated") or {}
    new_generated = graph.get("generated") or {}
    if (
        old_generated.get("managed_by") == MANAGED_BY
        and old_generated.get("inventory_digest") == new_generated.get("inventory_digest")
        and old_generated.get("generated_at")
    ):
        graph = copy.deepcopy(graph)
        graph["generated"]["generated_at"] = old_generated["generated_at"]
    return graph


def validate_relationship_graph(graph: Mapping[str, Any]) -> None:
    errors: list[str] = []
    if graph.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    audience = graph.get("audience")
    if audience not in {PUBLIC_AUDIENCE, PRIVATE_AUDIENCE}:
        errors.append("audience must be public or private")
    owner_data = graph.get("owner") or {}
    owner = str(owner_data.get("login") or "")
    if not owner:
        errors.append("owner.login is required")
    repositories = graph.get("repositories")
    relationships = graph.get("relationships")
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    if not isinstance(relationships, list):
        errors.append("relationships must be an array")
        relationships = []

    repo_names: set[str] = set()
    for index, repo in enumerate(repositories):
        if not isinstance(repo, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        full_name = str(repo.get("full_name") or "")
        if not full_name or "/" not in full_name:
            errors.append(f"repositories[{index}].full_name is invalid")
            continue
        key = full_name.casefold()
        if key in repo_names:
            errors.append(f"duplicate repository: {full_name}")
        repo_names.add(key)
        if audience == PUBLIC_AUDIENCE and repo.get("visibility") != "public":
            errors.append(f"public graph contains non-public repository: {full_name}")

    dotgithub = f"{owner}/.github".casefold()
    if owner and dotgithub not in repo_names:
        errors.append(f"missing organization registry repository {owner}/.github")

    edge_ids: set[str] = set()
    edge_keys: set[tuple[str, str, str]] = set()
    governed: set[str] = set()
    for index, edge in enumerate(relationships):
        if not isinstance(edge, dict):
            errors.append(f"relationships[{index}] must be an object")
            continue
        source = str(edge.get("from") or "")
        target = str(edge.get("to") or "")
        relationship_type = edge.get("type")
        if source.casefold() not in repo_names:
            errors.append(f"dangling relationship source: {source}")
        if target.casefold() not in repo_names:
            errors.append(f"dangling relationship target: {target}")
        if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
            errors.append(f"unsupported relationship type: {relationship_type}")
        if edge.get("status") not in ALLOWED_STATUSES:
            errors.append(f"unsupported relationship status: {edge.get('status')}")
        if edge.get("scope") not in ALLOWED_SCOPES:
            errors.append(f"unsupported relationship scope: {edge.get('scope')}")
        expected_id = relationship_id(edge)
        if edge.get("id") != expected_id:
            errors.append(f"relationship id mismatch for {source} {relationship_type} {target}")
        if expected_id in edge_ids:
            errors.append(f"duplicate relationship id: {expected_id}")
        edge_ids.add(expected_id)
        key = (source.casefold(), str(relationship_type), target.casefold())
        if key in edge_keys:
            errors.append(f"duplicate relationship: {source} {relationship_type} {target}")
        edge_keys.add(key)
        if source.casefold() == dotgithub and relationship_type == "governs":
            governed.add(target.casefold())

    for repo in repositories:
        full_name = str(repo.get("full_name") or "")
        if not full_name or full_name.casefold() == dotgithub:
            continue
        if str(repo.get("owner", "")).casefold() != owner.casefold():
            continue
        if full_name.casefold() not in governed:
            errors.append(f"missing governs relationship for sibling repository: {full_name}")

    if audience == PUBLIC_AUDIENCE:
        private_registry = graph.get("private_registry")
        if not isinstance(private_registry, dict):
            errors.append("public graph requires private_registry metadata")
        else:
            if private_registry.get("repository") != "approved-private-registry":
                errors.append("private_registry.repository must be approved-private-registry")
            if private_registry.get("path") != f"owners/{owner}.json":
                errors.append(f"private_registry.path must be owners/{owner}.json")
            private_digest = str(private_registry.get("digest") or "")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", private_digest):
                errors.append("private_registry.digest must be a SHA-256 digest")
            if not isinstance(private_registry.get("contains_non_public_inventory"), bool):
                errors.append("private_registry.contains_non_public_inventory must be boolean")

    generated = graph.get("generated") or {}
    if generated.get("managed_by") != MANAGED_BY:
        errors.append(f"generated.managed_by must be {MANAGED_BY}")
    digest_payload = {
        "schema_version": SCHEMA_VERSION,
        "owner": owner,
        "audience": audience,
        "repositories": repositories,
        "relationships": relationships,
        "unresolved_hints": graph.get("unresolved_hints", []),
    }
    expected_digest = sha256_prefixed(digest_payload)
    if generated.get("inventory_digest") != expected_digest:
        errors.append("generated.inventory_digest does not match graph content")

    serialized = canonical_json(graph)
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            errors.append("relationship graph contains a credential-shaped value")
            break
    if errors:
        raise RelationshipValidationError("; ".join(errors))


def render_relationship_markdown(graph: Mapping[str, Any]) -> str:
    owner = graph["owner"]["login"]
    repositories = graph.get("repositories", [])
    relationships = graph.get("relationships", [])
    hints = graph.get("unresolved_hints", [])
    lines = [
        f"# Repository relationships for `{owner}`",
        "",
        "This file is rendered from `repository-relationships.json`. The JSON registry is authoritative.",
        "",
        f"- Audience: `{graph['audience']}`",
        f"- Repositories represented: **{len(repositories)}**",
        f"- Relationships represented: **{len(relationships)}**",
        f"- Inventory digest: `{graph['generated']['inventory_digest']}`",
        "",
        "## Repositories",
        "",
        "| Repository | Visibility | Roles | Archived |",
        "|---|---|---|---|",
    ]
    for repo in repositories:
        roles = ", ".join(f"`{role}`" for role in repo.get("roles", []))
        lines.append(
            f"| `{repo['full_name']}` | `{repo['visibility']}` | {roles} | "
            f"{'yes' if repo.get('archived') else 'no'} |"
        )
    lines.extend(["", "## Relationships", ""])
    if relationships:
        lines.extend([
            "| From | Type | To | Status | Required |",
            "|---|---|---|---|---|",
        ])
        for edge in relationships:
            lines.append(
                f"| `{edge['from']}` | `{edge['type']}` | `{edge['to']}` | "
                f"`{edge['status']}` | {'yes' if edge.get('required') else 'no'} |"
            )
    else:
        lines.append("No relationships are currently declared beyond the registry repository itself.")
    lines.extend([
        "",
        "## Editing relationships",
        "",
        "Put reviewed public declarations in `repository-relationships.manual.json`; do not edit the generated registry directly.",
        "Private repository names and private-only relationships belong in the private `approved-private-registry` mirror.",
        "Inferred edges are advisory and must remain visibly labeled until reviewed.",
    ])
    if hints:
        lines.extend(["", "## Unresolved hints", ""])
        for hint in hints:
            candidates = ", ".join(f"`{item}`" for item in hint.get("candidates", []))
            lines.append(
                f"- `{hint['source']}` may `{hint['proposed_type']}` one of: {candidates}. "
                f"Reason: {hint['reason']}."
            )
    return "\n".join(lines).rstrip() + "\n"


def schema_document() -> dict[str, Any]:
    repo_schema = {
        "type": "object",
        "additionalProperties": True,
        "required": ["name", "full_name", "owner", "visibility", "default_branch", "archived", "fork", "roles", "source"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "full_name": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
            "owner": {"type": "string", "minLength": 1},
            "visibility": {"enum": ["public", "private", "internal"]},
            "default_branch": {"type": "string", "minLength": 1},
            "archived": {"type": "boolean"},
            "fork": {"type": "boolean"},
            "roles": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "source": {"type": "string", "minLength": 1},
        },
    }
    edge_schema = {
        "type": "object",
        "additionalProperties": True,
        "required": ["id", "from", "to", "type", "status", "scope", "required", "evidence"],
        "properties": {
            "id": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
            "from": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
            "to": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
            "type": {"enum": sorted(ALLOWED_RELATIONSHIP_TYPES)},
            "status": {"enum": sorted(ALLOWED_STATUSES)},
            "scope": {"enum": sorted(ALLOWED_SCOPES)},
            "required": {"type": "boolean"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "evidence": {"type": "array", "items": {"type": "object"}},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "private-registry://canonical/schema/repository-relationships.schema.json",
        "title": "Repository relationship registry",
        "type": "object",
        "additionalProperties": True,
        "required": ["schema_version", "owner", "audience", "generated", "repositories", "relationships", "unresolved_hints"],
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "audience": {"enum": [PUBLIC_AUDIENCE, PRIVATE_AUDIENCE]},
            "owner": {
                "type": "object",
                "required": ["login", "account_type", "dotgithub_repository", "linear_project"],
                "properties": {
                    "login": {"type": "string", "minLength": 1},
                    "account_type": {"enum": ["organization", "user"]},
                    "dotgithub_repository": {"type": "string"},
                    "linear_project": {"type": "object"},
                },
            },
            "generated": {
                "type": "object",
                "required": ["managed_by", "generator_version", "generated_at", "inventory_digest"],
                "properties": {
                    "managed_by": {"const": MANAGED_BY},
                    "inventory_digest": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
                },
            },
            "repositories": {"type": "array", "items": repo_schema},
            "relationships": {"type": "array", "items": edge_schema},
            "unresolved_hints": {"type": "array", "items": {"type": "object"}},
            "private_registry": {
                "type": "object",
                "additionalProperties": True,
                "required": ["repository", "path", "contains_non_public_inventory", "digest"],
                "properties": {
                    "repository": {"const": "approved-private-registry"},
                    "path": {"type": "string", "pattern": r"^owners/[^/]+\.json$"},
                    "contains_non_public_inventory": {"type": "boolean"},
                    "digest": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
                },
            },
        },
        "allOf": [
            {
                "if": {"properties": {"audience": {"const": PUBLIC_AUDIENCE}}},
                "then": {"required": ["private_registry"]},
            }
        ],
    }


def manual_schema_document() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "private-registry://canonical/schema/repository-relationships.manual.schema.json",
        "title": "Reviewed repository relationship declarations",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "owner", "repositories", "relationships"],
        "properties": {
            "$schema": {"type": "string"},
            "schema_version": {"const": SCHEMA_VERSION},
            "owner": {"type": "string", "minLength": 1},
            "repositories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": True,
                    "required": ["full_name", "visibility"],
                    "properties": {
                        "full_name": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
                        "visibility": {"enum": ["public", "private", "internal"]},
                    },
                },
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": True,
                    "required": ["from", "to", "type"],
                    "properties": {
                        "from": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
                        "to": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
                        "type": {"enum": sorted(ALLOWED_RELATIONSHIP_TYPES)},
                        "status": {"enum": sorted(ALLOWED_STATUSES)},
                        "scope": {"enum": sorted(ALLOWED_SCOPES)},
                    },
                },
            },
            "notes": {"type": "array", "items": {"type": "string"}},
        },
    }
