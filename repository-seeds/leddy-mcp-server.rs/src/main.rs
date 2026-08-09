//! Build-pinned, read-only MCP server for the canonical Leddy API documentation.
//!
//! The official Rust MCP SDK owns JSON-RPC framing, lifecycle negotiation,
//! cancellation, request routing, typed argument validation, and stdio
//! transport. The server performs no network requests, accepts no credentials,
//! executes no HTTP operations, and reserves stdout for MCP frames.

use std::collections::BTreeSet;

use rmcp::{
    ErrorData, ServerHandler, ServiceExt,
    handler::server::{router::tool::ToolRouter, wrapper::Parameters},
    model::{Implementation, ServerCapabilities, ServerInfo, ToolAnnotations},
    tool, tool_handler, tool_router,
    transport::stdio,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

const SERVER_NAME: &str = "leddy-mcp-server";
const API_REPOSITORY: &str = "led-dynamo/leddy-api-server.rs";
const MCP_REPOSITORY: &str = "led-dynamo/leddy-mcp-server.rs";
const API_SOURCE_HEAD: &str = "aea63f652a20c087260bab3c86b31baa80eaa7ea";
const OPENAPI_SHA256: &str = "cf0be66ce0ebb02c3fc077a88c3129c55b4d05f30070b3c7186d13731ae7fe88";
const MAX_OUTPUT_BYTES: usize = 512 * 1024;
const MANIFEST_JSON: &str = include_str!("../openapi/api-docs.manifest.json");
const OPENAPI_JSON: &str = include_str!("../openapi/leddy.openapi.json");
const REQUIRED_TOOLS: [&str; 5] = [
    "api_docs_discover",
    "api_docs_get_openapi",
    "api_docs_validate",
    "api_docs_list_operations",
    "api_docs_describe_operation",
];
const ZED_DEPENDENCIES: [&str; 6] = [
    "led-dynamo/leddy-clients",
    "led-dynamo/leddy-interfaces",
    "led-dynamo/leddy-lib",
    "led-dynamo/leddy-cli",
    "led-dynamo/leddy-sync",
    "shared-auth/shared-auth-clients",
];

#[derive(Clone)]
struct LeddyMcp {
    tool_router: ToolRouter<Self>,
}

impl LeddyMcp {
    fn new() -> Self {
        let mut tool_router = Self::tool_router();
        for route in tool_router.map.values_mut() {
            route.attr.annotations = Some(
                ToolAnnotations::new()
                    .read_only(true)
                    .destructive(false)
                    .idempotent(true)
                    .open_world(false),
            );
        }
        Self { tool_router }
    }
}

impl Default for LeddyMcp {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Clone, Copy, Debug, Deserialize, JsonSchema, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
enum Stability {
    Stable,
    Beta,
    Experimental,
}

impl Stability {
    const fn as_str(self) -> &'static str {
        match self {
            Self::Stable => "stable",
            Self::Beta => "beta",
            Self::Experimental => "experimental",
        }
    }
}

#[derive(Debug, Default, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
struct ListOperationsRequest {
    /// Optional exact OpenAPI tag filter.
    tag: Option<String>,
    /// Optional MCP catalog exposure filter.
    mcp_exposed: Option<bool>,
    /// Optional HTTP mutation-classification filter.
    mutating: Option<bool>,
    /// Optional stability filter.
    stability: Option<Stability>,
}

#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
struct DescribeOperationRequest {
    /// Exact OpenAPI operationId.
    operation_id: String,
}

#[derive(Clone, Debug, Serialize)]
struct NormalizedOperation {
    operation_id: String,
    method: String,
    path: String,
    summary: String,
    description: Option<String>,
    tags: Vec<String>,
    visibility: String,
    stability: String,
    mcp_exposed: bool,
    mutating: bool,
}

#[tool_router]
impl LeddyMcp {
    #[tool(
        description = "Return the validated ore.api-docs.v1 discovery manifest, immutable API-source provenance, and canonical Zed dependency graph. Read-only and offline."
    )]
    fn api_docs_discover(&self) -> Result<String, ErrorData> {
        let manifest = parse_manifest()?;
        render(&json!({
            "manifest": manifest,
            "snapshot": snapshot_metadata(),
            "zed": {
                "materializationDirectory": ".vendor/.zed",
                "dependencies": ZED_DEPENDENCIES,
                "submoduleInterop": {
                    "gitAuthority": "exact committed checkout and source transport",
                    "zedAuthority": "package identity, dependency intent, materialization, and immutable lock provenance",
                    "adoptionCommand": "zed overtake --git-submodules"
                }
            }
        }))
    }

    #[tool(
        description = "Return the bounded build-pinned public OpenAPI 3.1 document and exact SHA-256 provenance. This tool performs no HTTP request."
    )]
    fn api_docs_get_openapi(&self) -> Result<String, ErrorData> {
        let openapi = parse_openapi()?;
        render(&json!({
            "sha256": OPENAPI_SHA256,
            "mediaType": "application/vnd.oai.openapi+json;version=3.1",
            "bytes": OPENAPI_JSON.len(),
            "snapshot": snapshot_metadata(),
            "document": openapi
        }))
    }

    #[tool(
        description = "Validate the embedded manifest, OpenAPI version, digest declaration, operation metadata, same-organization pairing, and zero executable mutations."
    )]
    fn api_docs_validate(&self) -> Result<String, ErrorData> {
        render(&validation_report()?)
    }

    #[tool(
        description = "List normalized API operations with optional tag, stability, MCP-exposure, and mutation filters. Metadata only; no API operation is invoked."
    )]
    fn api_docs_list_operations(
        &self,
        Parameters(request): Parameters<ListOperationsRequest>,
    ) -> Result<String, ErrorData> {
        if let Some(tag) = request.tag.as_deref() {
            validate_tag(tag)?;
        }

        let stability = request.stability.map(Stability::as_str);
        let operations = normalized_operations()?
            .into_iter()
            .filter(|operation| {
                request
                    .tag
                    .as_deref()
                    .is_none_or(|tag| operation.tags.iter().any(|candidate| candidate == tag))
            })
            .filter(|operation| {
                request
                    .mcp_exposed
                    .is_none_or(|wanted| operation.mcp_exposed == wanted)
            })
            .filter(|operation| {
                request
                    .mutating
                    .is_none_or(|wanted| operation.mutating == wanted)
            })
            .filter(|operation| {
                stability.is_none_or(|wanted| operation.stability == wanted)
            })
            .collect::<Vec<_>>();

        render(&json!({
            "count": operations.len(),
            "operations": operations,
            "executionPerformed": false,
            "snapshot": snapshot_metadata()
        }))
    }

    #[tool(
        description = "Describe one operation by exact operationId, including exposure and mutation metadata. The operation is never executed."
    )]
    fn api_docs_describe_operation(
        &self,
        Parameters(request): Parameters<DescribeOperationRequest>,
    ) -> Result<String, ErrorData> {
        validate_operation_id(&request.operation_id)?;
        let operation = normalized_operations()?
            .into_iter()
            .find(|operation| operation.operation_id == request.operation_id)
            .ok_or_else(|| ErrorData::invalid_params("operation_id was not found", None));

        render(&json!({
            "operation": operation,
            "execution": {
                "permitted": false,
                "performed": false,
                "reason": "ore.api-docs.v1 baseline tools describe documentation only"
            },
            "snapshot": snapshot_metadata()
        }))
    }
}

#[tool_handler(router = self.tool_router)]
impl ServerHandler for LeddyMcp {
    fn get_info(&self) -> ServerInfo {
        ServerInfo::new(ServerCapabilities::builder().enable_tools().build())
            .with_server_info(Implementation::new(SERVER_NAME, env!("CARGO_PKG_VERSION")))
            .with_instructions(
                "Read-only, build-pinned Leddy API documentation. No tool sends HTTP requests, accepts credentials, reads device state, opens WebSockets, or mutates displays.",
            )
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let service = LeddyMcp::new().serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}

fn parse_manifest() -> Result<Value, ErrorData> {
    serde_json::from_str(MANIFEST_JSON)
        .map_err(|_| ErrorData::internal_error("embedded API-docs manifest is invalid", None))
}

fn parse_openapi() -> Result<Value, ErrorData> {
    serde_json::from_str(OPENAPI_JSON)
        .map_err(|_| ErrorData::internal_error("embedded OpenAPI document is invalid", None))
}

fn snapshot_metadata() -> Value {
    json!({
        "mode": "build-pinned",
        "apiRepository": API_REPOSITORY,
        "apiHead": API_SOURCE_HEAD,
        "mcpRepository": MCP_REPOSITORY,
        "openapiSha256": OPENAPI_SHA256,
        "networkAccess": false,
        "credentialsAccepted": false
    })
}

fn render(value: &Value) -> Result<String, ErrorData> {
    let text = serde_json::to_string_pretty(value)
        .map_err(|_| ErrorData::internal_error("tool result serialization failed", None))?;
    if text.len() > MAX_OUTPUT_BYTES {
        return Err(ErrorData::internal_error(
            "tool result exceeded the configured output limit",
            None,
        ));
    }
    Ok(text)
}

fn normalized_operations() -> Result<Vec<NormalizedOperation>, ErrorData> {
    let openapi = parse_openapi()?;
    let paths = openapi
        .get("paths")
        .and_then(Value::as_object)
        .ok_or_else(|| ErrorData::internal_error("OpenAPI paths must be an object", None))?;
    let mut operations = Vec::new();

    for (path, item) in paths {
        let item = item
            .as_object()
            .ok_or_else(|| ErrorData::internal_error("OpenAPI path item must be an object", None))?;
        for method in [
            "get", "put", "post", "delete", "options", "head", "patch", "trace",
        ] {
            let Some(operation) = item.get(method) else {
                continue;
            };
            let operation_id = required_string(operation, "operationId")?;
            let summary = required_string(operation, "summary")?;
            let tags = operation
                .get("tags")
                .and_then(Value::as_array)
                .ok_or_else(|| ErrorData::internal_error("operation tags must be an array", None))?
                .iter()
                .map(|tag| {
                    tag.as_str()
                        .filter(|value| !value.is_empty())
                        .map(ToOwned::to_owned)
                        .ok_or_else(|| {
                            ErrorData::internal_error(
                                "operation tags must contain non-empty strings",
                                None,
                            )
                        })
                })
                .collect::<Result<Vec<_>, _>>()?;
            if tags.is_empty() {
                return Err(ErrorData::internal_error(
                    "operation must contain at least one tag",
                    None,
                ));
            }

            let visibility = required_string(operation, "x-ore-visibility")?;
            let stability = required_string(operation, "x-ore-stability")?;
            let mcp_exposed = required_bool(operation, "x-ore-mcp-expose")?;
            let mutating = required_bool(operation, "x-ore-mcp-mutating")?;

            operations.push(NormalizedOperation {
                operation_id,
                method: method.to_ascii_uppercase(),
                path: path.clone(),
                summary,
                description: operation
                    .get("description")
                    .and_then(Value::as_str)
                    .map(ToOwned::to_owned),
                tags,
                visibility,
                stability,
                mcp_exposed,
                mutating,
            });
        }
    }

    operations.sort_by(|left, right| left.operation_id.cmp(&right.operation_id));
    Ok(operations)
}

fn required_string(value: &Value, field: &str) -> Result<String, ErrorData> {
    value
        .get(field)
        .and_then(Value::as_str)
        .filter(|candidate| !candidate.is_empty())
        .map(ToOwned::to_owned)
        .ok_or_else(|| {
            ErrorData::internal_error(format!("operation field {field} must be a string"), None)
        })
}

fn required_bool(value: &Value, field: &str) -> Result<bool, ErrorData> {
    value.get(field).and_then(Value::as_bool).ok_or_else(|| {
        ErrorData::internal_error(format!("operation field {field} must be Boolean"), None)
    })
}

fn validation_report() -> Result<Value, ErrorData> {
    let manifest = parse_manifest()?;
    let openapi = parse_openapi()?;
    let operations = normalized_operations()?;
    let operation_ids = operations
        .iter()
        .map(|operation| operation.operation_id.as_str())
        .collect::<BTreeSet<_>>();
    let exposed = operations
        .iter()
        .filter(|operation| operation.mcp_exposed)
        .map(|operation| operation.operation_id.as_str())
        .collect::<Vec<_>>();
    let exposed_mutations = operations
        .iter()
        .filter(|operation| operation.mcp_exposed && operation.mutating)
        .count();

    let paths_are_root_relative = manifest_paths(&manifest)?
        .iter()
        .all(|path| is_safe_root_relative_path(path));
    let method_classification_matches = operations.iter().all(|operation| {
        operation.mutating
            == !matches!(operation.method.as_str(), "GET" | "HEAD" | "OPTIONS")
    });
    let manifest_tools = manifest
        .pointer("/mcp/tools")
        .and_then(Value::as_array)
        .ok_or_else(|| ErrorData::internal_error("manifest MCP tools must be an array", None))?
        .iter()
        .map(|value| {
            value
                .as_str()
                .map(ToOwned::to_owned)
                .ok_or_else(|| ErrorData::internal_error("manifest tool must be a string", None))
        })
        .collect::<Result<Vec<_>, _>>()?;
    let expected_tools = REQUIRED_TOOLS
        .iter()
        .map(|value| (*value).to_owned())
        .collect::<Vec<_>>();

    let checks = json!({
        "schemaVersion": manifest["schemaVersion"] == "ore.api-docs.v1",
        "openapi31": openapi["openapi"]
            .as_string()
            .is_some_and(|version| version.starts_with("3.1.")),
        "declaredDigest": manifest["public"]["openapi"]["sha256"] == OPENAPI_SHA256,
        "sameOrganizationPair": manifest["mcp"]["repository"] == MCP_REPOSITORY,
        "readOnlyPairing": manifest["mcp"]["mode"] == "read-only",
        "internalUnavailable": manifest["internal"]["available"] == false,
        "safeRootRelativePaths": paths_are_root_relative,
        "exactToolCatalog": manifest_tools == expected_tools,
        "sixOperations": operations.len() == 6,
        "uniqueOperationIds": operation_ids.len() == operations.len(),
        "httpMutationClassification": method_classification_matches,
        "zeroExposedMutations": exposed_mutations == 0,
        "healthOnlyExposure": exposed == ["getHealth"],
        "websocketNotExposed": operations.iter().any(|operation| {
            operation.operation_id == "connectDeviceWebSocket" && !operation.mcp_exposed
        }),
        "deviceStateNotExposed": operations.iter()
            .filter(|operation| matches!(
                operation.operation_id.as_str(),
                "listDevices" | "getDevice"
            ))
            .all(operation | !operation.mcp_exposed),
        "snapshotApiHeadRecorded": API_SOURCE_HEAD.len() == 40
            && API_SOURCE_HEAD.bytes().all(|byte| byte.is_ascii_hexdigit())
    });
    let valid = checks
        .as_object()
        .expect("checks are an object")
        .values()
        .all(|value| value == true);

    Ok(json!({
        "valid": valid,
        "checks": checks,
        "operationCount": operations.len(),
        "exposedOperationIds": exposed,
        "exposedMutationCount": exposed_mutations,
        "snapshot": snapshot_metadata(),
        "digestVerification": {
            "mode": "build-pinned-ci",
            "expectedSha256": OPENAPI_SHA256,
            "bytes": OPENAPI_JSON.len()
        }
    }))
}

fn manifest_paths(manifest: &Value) -> Result<Vec<String>, ErrorData> {
    let mut paths = Vec::new();
    for pointer in ["/public/openapi/path", "/public/ui/path"] {
        paths.push(
            manifest
                .pointer(pointer)
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    ErrorData::internal_error("manifest canonical path is missing", None)
                })?
                .to_owned(),
        );
    }
    for pointer in ["/public/openapi/aliases", "/public/ui/aliases"] {
        let aliases = manifest
            .pointer(pointer)
            .and_then(Value::as_array)
            .ok_or_else(|| ErrorData::internal_error("manifest aliases are missing", None))?;
        for alias in aliases {
            paths.push(
                alias
                    .as_str()
                    .ok_or_else(|| {
                        ErrorData::internal_error("manifest alias must be a string", None)
                    })?
                    .to_owned(),
            );
        }
    }
    Ok(paths)
}

fn is_safe_root_relative_path(path: &str) -> bool {
    path.starts_with('/')
        && !path.starts_with("//")
        && !path.contains('?')
        && !path.contains('#')
        && !path.contains('\\')
        && !path.contains("://")
        && !path.contains('@')
}

fn validate_tag(tag: &str) -> Result<(), ErrorData> {
    if tag.is_empty()
        || tag.len() > 64
        || !tag
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.'))
    {
        return Err(ErrorData::invalid_params("tag is invalid", None));
    }
    Ok(())
}

fn validate_operation_id(operation_id: &str) -> Result<(), ErrorData> {
    if operation_id.is_empty()
        || operation_id.len() > 128
        || !operation_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.'))
    {
        return Err(ErrorData::invalid_params(
            "operation_id is invalid",
            None,
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tool_catalog_is_exact_closed_and_read_only() {
        let server = LeddyMcp::new();
        let mut names = server
            .tool_router
            .map
            .keys()
            .map(|name| name.as_ref())
            .collect::<Vec<_>>();
        names.sort_unstable();
        let mut expected = REQUIRED_TOOLS;
        expected.sort_unstable();
        assert_eq!(names, expected);

        for route in server.tool_router.map.values() {
            let annotations = route.attr.annotations.as_ref().expect("annotations");
            assert_eq!(annotations.read_only_hint, Some(true));
            assert_eq!(annotations.destructive_hint, Some(false));
            assert_eq!(annotations.idempotent_hint, Some(true));
            assert_eq!(annotations.open_world_hint, Some(false));
        }
    }

    #[test]
    fn embedded_snapshot_is_valid_and_health_is_the_only_exposed_operation() {
        let report = validation_report().expect("valid report");
        assert_eq!(report["valid"], true);
        assert_eq!(report["operationCount"], 6);
        assert_eq!(report["exposedOperationIds"], json!(["getHealth"]));
        assert_eq!(report["exposedMutationCount"], 0);
    }

    #[test]
    fn operation_filters_and_descriptions_remain_metadata_only() {
        let operations = normalized_operations().expect("operations");
        assert_eq!(
            operations
                .iter()
                .filter(|operation| !operation.mutating)
                .count(),
            4
        );
        let websocket = operations
            .iter()
            .find(|operation| operation.operation_id == "connectDeviceWebSocket")
            .expect("websocket operation");
        assert!(!websocket.mcp_exposed);
        assert!(!websocket.mutating);
    }

    #[test]
    fn unsafe_manifest_paths_are_rejected() {
        for path in [
            "https://example.com/openapi.json",
            "//example.com/openapi.json",
            "/openapi.json?token=secret",
            "/openapi.json#fragment",
            "/\\server\\share",
        ] {
            assert!(!is_safe_root_relative_path(path), "{path}");
        }
        assert!(is_safe_root_relative_path("/openapi.json"));
    }
}
