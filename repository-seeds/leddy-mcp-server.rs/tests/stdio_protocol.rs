use std::{
    io::{BufRead, BufReader, Read, Write},
    process::{Command, Stdio},
    sync::mpsc,
    thread,
    time::Duration,
};

use serde_json::{Value, json};

const REQUIRED_TOOLS: [&str; 5] = [
    "api_docs_describe_operation",
    "api_docs_discover",
    "api_docs_get_openapi",
    "api_docs_list_operations",
    "api_docs_validate",
];

fn send(stdin: &mut impl Write, value: &Value) {
    serde_json::to_writer(&mut *stdin, value).expect("serialize request");
    stdin.write_all(b"\n").expect("write newline");
    stdin.flush().expect("flush request");
}

fn receive(receiver: &mpsc::Receiver<String>) -> Value {
    let line = receiver
        .recv_timeout(Duration::from_secs(15))
        .expect("server response before timeout");
    serde_json::from_str(&line).expect("stdout contains one JSON protocol frame")
}

fn tool_text(response: &Value) -> Value {
    let text = response["result"]["content"][0]["text"]
        .as_str()
        .expect("tool returns a text content block");
    serde_json::from_str(text).expect("tool text is JSON")
}

#[test]
fn official_stdio_server_exposes_only_the_five_read_only_api_docs_tools() {
    let mut child = Command::new(env!("CARGO_BIN_EXE_leddy-mcp-server"))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn Leddy MCP server");
    let mut stdin = child.stdin.take().expect("stdin pipe");
    let stdout = child.stdout.take().expect("stdout pipe");
    let (sender, receiver) = mpsc::channel();
    thread::spawn(move || {
        for line in BufReader::new(stdout).lines() {
            match line {
                Ok(line) if sender.send(line).is_ok() => {}
                _ => break,
            }
        }
    });

    send(
        &mut stdin,
        &json!({
            "jsonrpc": "2.0",
            "id": "initialize",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "leddy-contract-test", "version": "1.0.0"}
            }
        }),
    );
    let initialized = receive(&receiver);
    assert_eq!(initialized["jsonrpc"], "2.0");
    assert_eq!(initialized["id"], "initialize");
    assert_eq!(initialized["result"]["protocolVersion"], "2025-11-25");
    assert_eq!(
        initialized["result"]["serverInfo"]["name"],
        "leddy-mcp-server"
    );

    send(
        &mut stdin,
        &json!({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }),
    );
    assert!(matches!(
        receiver.recv_timeout(Duration::from_millis(200)),
        Err(mpsc::RecvTimeoutError::Timeout)
    ));

    send(
        &mut stdin,
        &json!({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
    );
    let tools = receive(&receiver);
    let mut names = Vec::new();
    for tool in tools["result"]["tools"]
        .as_array()
        .expect("tools array")
    {
        names.push(tool["name"].as_str().expect("tool name").to_owned());
        assert!(tool["description"].as_str().is_some_and(|value| !value.is_empty()));
        assert_eq!(tool["inputSchema"]["type"], "object");
        assert_eq!(tool["annotations"]["readOnlyHint"], true);
        assert_eq!(tool["annotations"]["destructiveHint"], false);
        assert_eq!(tool["annotations"]["idempotentHint"], true);
        assert_eq!(tool["annotations"]["openWorldHint"], false);
    }
    names.sort();
    assert_eq!(names, REQUIRED_TOOLS);

    send(
        &mut stdin,
        &json!({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "api_docs_validate", "arguments": {}}
        }),
    );
    let validation = receive(&receiver);
    assert_eq!(validation["result"]["isError"], false);
    let validation = tool_text(&validation);
    assert_eq!(validation["valid"], true);
    assert_eq!(validation["operationCount"], 6);
    assert_eq!(validation["exposedMutationCount"], 0);
    assert_eq!(validation["exposedOperationIds"], json!(["getHealth"]));

    send(
        &mut stdin,
        &json!({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "api_docs_describe_operation",
                "arguments": {"operation_id": "connectDeviceWebSocket"}
            }
        }),
    );
    let described = tool_text(&receive(&receiver));
    assert_eq!(described["operation"]["operation_id"], "connectDeviceWebSocket");
    assert_eq!(described["operation"]["mcp_exposed"], false);
    assert_eq!(described["execution"]["permitted"], false);
    assert_eq!(described["execution"]["performed"], false);

    send(
        &mut stdin,
        &json!({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "api_docs_list_operations",
                "arguments": {"mcp_exposed": true, "unexpected": true}
            }
        }),
    );
    let invalid = receive(&receiver);
    assert_eq!(invalid["jsonrpc"], "2.0");
    assert_eq!(invalid["id"], 5);
    assert!(invalid.get("error").is_some() || invalid["result"]["isError"] == true);

    drop(stdin);
    let _ = child.kill();
    let _ = child.wait();
    let mut stderr = String::new();
    child
        .stderr
        .take()
        .expect("stderr pipe")
        .read_to_string(&mut stderr)
        .expect("read stderr");
    assert!(!stderr.contains("2024-11-05"));
    assert!(!stderr.contains("method not found:"));
}
