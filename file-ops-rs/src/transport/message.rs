/// JSON-RPC 2.0 message types for MCP protocol

use serde::{Deserialize, Serialize};
use serde_json::Value;

/// JSON-RPC 2.0 request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonRpcRequest {
    pub jsonrpc: String,
    pub id: RequestId,
    pub method: String,
    #[serde(default)]
    pub params: Value,
}

/// Request ID (number or string)
#[derive(Debug, Clone, Serialize, Deserialize, Hash, PartialEq, Eq)]
#[serde(untagged)]
pub enum RequestId {
    Number(u64),
    String(String),
}

impl RequestId {
    pub fn as_json(&self) -> Value {
        match self {
            RequestId::Number(n) => Value::Number((*n).into()),
            RequestId::String(s) => Value::String(s.clone()),
        }
    }
}

/// JSON-RPC 2.0 response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonRpcResponse {
    pub jsonrpc: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<RequestId>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<JsonRpcError>,
}

/// JSON-RPC 2.0 error
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonRpcError {
    pub code: i32,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,
}

impl JsonRpcResponse {
    pub fn success(id: RequestId, result: Value) -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id: Some(id),
            result: Some(result),
            error: None,
        }
    }

    pub fn error(id: Option<RequestId>, code: i32, message: impl Into<String>) -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id,
            result: None,
            error: Some(JsonRpcError {
                code,
                message: message.into(),
                data: None,
            }),
        }
    }

    pub fn parse_error() -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id: None,
            result: None,
            error: Some(JsonRpcError {
                code: -32700,
                message: "Parse error".to_string(),
                data: None,
            }),
        }
    }

    pub fn invalid_request(reason: impl Into<String>) -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id: None,
            result: None,
            error: Some(JsonRpcError {
                code: -32600,
                message: format!("Invalid request: {}", reason.into()),
                data: None,
            }),
        }
    }

    pub fn method_not_found(method: impl Into<String>) -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id: None,
            result: None,
            error: Some(JsonRpcError {
                code: -32601,
                message: format!("Method not found: {}", method.into()),
                data: None,
            }),
        }
    }

    pub fn internal_error(reason: impl Into<String>) -> Self {
        JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            id: None,
            result: None,
            error: Some(JsonRpcError {
                code: -32603,
                message: format!("Internal error: {}", reason.into()),
                data: None,
            }),
        }
    }
}
