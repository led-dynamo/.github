use serde_json::{Value, json};
use std::io::{self, BufRead, Write};

const SERVER_NAME: &str = "leddy-mcp-server";
const ORGANIZATION: &str = "led-dynamo";
const REPOSITORY: &str = "led-dynamo/leddy-mcp-server.rs";
const PROTOCOL_VERSION: &str = "2025-06-18";
const ZED_DEPENDENCIES: [&str; 6] = [
    "led-dynamo/leddy-clients",
    "led-dynamo/leddy-interfaces",
    "led-dynamo/leddy-lib",
    "led-dynamo/leddy-cli",
    "led-dynamo/leddy-sync",
    "shared-auth/shared-auth-clients",
];

fn success(id: Value, result: Value) -> Value {
    json!({"jsonrpc": "2.0", "id": id, "result": result})
}

fn failure(id: Value, code: i64, message: impl Into<String>) -> Value {
    json!({
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": code, "message": message.into()}
    })
}

fn dependency_graph() -> Value {
    json!({
        "organization": ORGANIZATION,
        "repository": REPOSITORY,
        "package": SERVER_NAME,
        "materializationDirectory": ".vendor/.zed",
        "dependencies": ZED_DEPENDENCIES,
        "submoduleInterop": {
            "gitAuthority": "exact committed checkout and source transport",
            "zedAuthority": "package identity, dependency intent, materialization, and lock provenance",
            "adoptionCommand": "zed overtake --git-submodules"
        }
    })
}

fn tool_result() -> Value {
    let graph = dependency_graph();
    let text = serde_json::to_string_pretty(&graph).expect("dependency graph is serializable");
    json!({
        "content": [{"type": "text", "text": text}],
        "structuredContent": graph,
        "isError": false
    })
}

fn handle_message(message: Value) -> Option<Value> {
    let id = message.get("id").cloned();
    let Some(method) = message.get("method").and_then(Value::as_str) else {
        return id.map(|id| failure(id, -32600, "request method is required"));
    };

    match method {
        "initialize" => id.map(|id| {
            success(
                id,
                json!({
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": false}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "title": "Leddy MCP Server",
                        "version": env!("CARGO_PKG_VERSION")
                    },
                    "instructions": "Use zed_dependency_graph to inspect canonical package and submodule ownership."
                }),
            )
        }),
        "notifications/initialized" | "notifications/cancelled" => None,
        "ping" => id.map(|id| success(id, json!({}))),
        "tools/list" => id.map(|id| {
            success(
                id,
                json!({
                    "tools": [{
                        "name": "zed_dependency_graph",
                        "title": "Zed dependency graph",
                        "description": "Return canonical Leddy package dependencies and Git-submodule ownership rules.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": false
                        }
                    }]
                }),
            )
        }),
        "tools/call" => {
            let id = id?;
            match message.pointer("/params/name").and_then(Value::as_str) {
                Some("zed_dependency_graph") => Some(success(id, tool_result())),
                Some(name) => Some(failure(id, -32602, format!("unknown tool: {name}"))),
                None => Some(failure(id, -32602, "tool name is required")),
            }
        }
        _ => id.map(|id| failure(id, -32601, format!("method not found: {method}"))),
    }
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut writer = io::BufWriter::new(stdout.lock());

    for line in stdin.lock().lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }

        let response = match serde_json::from_str::<Value>(&line) {
            Ok(message) => handle_message(message),
            Err(error) => Some(failure(
                Value::Null,
                -32700,
                format!("parse error: {error}"),
            )),
        };

        if let Some(response) = response {
            serde_json::to_writer(&mut writer, &response).map_err(io::Error::other)?;
            writer.write_all(b"\n")?;
            writer.flush()?;
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initialize_returns_supported_protocol() {
        let response = handle_message(json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0.1.0"}
            }
        }))
        .expect("initialize request should receive a response");

        assert_eq!(response["result"]["protocolVersion"], PROTOCOL_VERSION);
        assert_eq!(response["result"]["serverInfo"]["name"], SERVER_NAME);
    }

    #[test]
    fn dependency_tool_returns_complete_graph() {
        let response = handle_message(json!({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "zed_dependency_graph", "arguments": {}}
        }))
        .expect("tool request should receive a response");

        let dependencies = response["result"]["structuredContent"]["dependencies"]
            .as_array()
            .expect("dependencies should be an array");
        assert_eq!(dependencies.len(), ZED_DEPENDENCIES.len());
        assert!(dependencies.iter().any(|value| {
            value.as_str() == Some("shared-auth/shared-auth-clients")
        }));
    }

    #[test]
    fn notifications_do_not_emit_responses() {
        assert!(
            handle_message(json!({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }))
            .is_none()
        );
    }
}
