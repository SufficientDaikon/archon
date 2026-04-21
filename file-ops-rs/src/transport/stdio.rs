/// Async JSON-RPC 2.0 stdio transport
///
/// Implements MCP protocol over stdin/stdout with newline-delimited JSON-RPC 2.0 messages.
/// Critical invariant: Responses go ONLY to stdout. Diagnostics go to stderr.

use crate::errors::Result;
use dashmap::DashMap;
use serde_json::Value;
use std::io;
use std::sync::Arc;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, BufWriter};
use tokio::sync::Mutex;

use super::message::{JsonRpcRequest, JsonRpcResponse, RequestId};

pub struct StdioTransport {
    reader: Arc<Mutex<BufReader<io::Stdin>>>,
    writer: Arc<Mutex<BufWriter<io::Stdout>>>,
    request_tracker: Arc<DashMap<String, Instant>>,
}

impl StdioTransport {
    pub fn new() -> Self {
        let stdin = io::stdin();
        let stdout = io::stdout();

        StdioTransport {
            reader: Arc::new(Mutex::new(BufReader::new(stdin))),
            writer: Arc::new(Mutex::new(BufWriter::new(stdout))),
            request_tracker: Arc::new(DashMap::new()),
        }
    }

    /// Read next JSON-RPC request from stdin
    pub async fn read_request(&self) -> Result<JsonRpcRequest> {
        let mut reader = self.reader.lock().await;
        let mut line = String::new();

        loop {
            line.clear();
            match reader.read_line(&mut line).await? {
                0 => {
                    // EOF
                    return Err(crate::errors::FileOpsError::Internal(
                        "EOF on stdin".to_string(),
                    ));
                }
                _ => {
                    let trimmed = line.trim();
                    if !trimmed.is_empty() {
                        break;
                    }
                }
            }
        }

        // Parse JSON-RPC request
        let request: JsonRpcRequest = serde_json::from_str(&line)
            .map_err(|e| crate::errors::FileOpsError::JsonError(e))?;

        // Validate JSON-RPC 2.0 format
        if request.jsonrpc != "2.0" {
            return Err(crate::errors::FileOpsError::InvalidRequest(
                "jsonrpc field must be '2.0'".to_string(),
            ));
        }

        // Track request for metrics
        let request_id_str = format!("{:?}", request.id);
        self.request_tracker.insert(request_id_str, Instant::now());

        // Log to stderr (never to stdout!)
        eprintln!("[REQUEST] id={:?} method={}", request.id, request.method);

        Ok(request)
    }

    /// Send JSON-RPC response to stdout
    pub async fn send_response(&self, response: JsonRpcResponse) -> Result<()> {
        let mut writer = self.writer.lock().await;

        // Serialize response
        let json = serde_json::to_string(&response)?;

        // Write to stdout with newline
        writer.write_all(json.as_bytes()).await?;
        writer.write_all(b"\n").await?;
        writer.flush().await?;

        // Log to stderr
        if let Some(id) = &response.id {
            if response.error.is_some() {
                eprintln!(
                    "[ERROR RESPONSE] id={:?} error={}",
                    id,
                    response
                        .error
                        .as_ref()
                        .map(|e| &e.message)
                        .unwrap_or(&"unknown".to_string())
                );
            } else {
                eprintln!("[SUCCESS RESPONSE] id={:?}", id);
            }
        }

        Ok(())
    }

    /// Get request latency (for metrics)
    pub fn get_request_latency(&self, id: &RequestId) -> Option<u128> {
        let id_str = format!("{:?}", id);
        self.request_tracker.remove(&id_str).map(|(_, start)| {
            start.elapsed().as_millis()
        })
    }

    /// Clear old request tracking entries (housekeeping)
    pub fn cleanup_old_requests(&self) {
        let now = Instant::now();
        self.request_tracker
            .retain(|_, start| now.duration_since(*start).as_secs() < 300); // Keep 5 min
    }
}

impl Clone for StdioTransport {
    fn clone(&self) -> Self {
        StdioTransport {
            reader: Arc::clone(&self.reader),
            writer: Arc::clone(&self.writer),
            request_tracker: Arc::clone(&self.request_tracker),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_message_serialization() {
        let response = JsonRpcResponse::success(
            RequestId::Number(1),
            serde_json::json!({"result": "success"}),
        );

        let json = serde_json::to_string(&response).unwrap();
        assert!(json.contains("\"jsonrpc\":\"2.0\""));
        assert!(json.contains("\"id\":1"));
    }
}
