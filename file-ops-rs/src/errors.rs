/// Error types for file-ops MCP server
use serde_json::json;
use thiserror::Error;

pub type Result<T> = std::result::Result<T, FileOpsError>;

#[derive(Debug, Error)]
pub enum FileOpsError {
    #[error("File not found: {0}")]
    FileNotFound(String),

    #[error("Is a directory: {0}")]
    IsDirectory(String),

    #[error("Out of bounds: line {actual} not in range 1-{total}")]
    OutOfBounds { actual: usize, total: usize },

    #[error("External change detected: hash {actual} != expected {expected}")]
    ExternalChange { expected: String, actual: String },

    #[error("Invalid regex pattern: {0}")]
    InvalidRegex(String),

    #[error("Rate limit exceeded")]
    RateLimitExceeded,

    #[error("Schema validation failed: {0}")]
    SchemaValidation(String),

    #[error("Parent directory does not exist: {0}")]
    NoParentDir(String),

    #[error("File already exists: {0}")]
    FileExists(String),

    #[error("Parent directory creation failed: {0}")]
    DirCreationFailed(String),

    #[error("Encoding error: {0}")]
    EncodingError(String),

    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::error::Error),

    #[error("Unicode error: {0}")]
    UnicodeError(String),

    #[error("Invalid request: {0}")]
    InvalidRequest(String),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl FileOpsError {
    /// Convert to JSON-RPC 2.0 error response
    pub fn to_json_rpc_error(&self) -> serde_json::Value {
        let code = match self {
            FileOpsError::FileNotFound(_) => -32001,
            FileOpsError::IsDirectory(_) => -32002,
            FileOpsError::OutOfBounds { .. } => -32003,
            FileOpsError::ExternalChange { .. } => -32004,
            FileOpsError::InvalidRegex(_) => -32005,
            FileOpsError::RateLimitExceeded => -32006,
            FileOpsError::SchemaValidation(_) => -32007,
            FileOpsError::NoParentDir(_) => -32008,
            FileOpsError::FileExists(_) => -32009,
            FileOpsError::DirCreationFailed(_) => -32010,
            FileOpsError::EncodingError(_) => -32011,
            FileOpsError::IoError(_) => -32012,
            FileOpsError::JsonError(_) => -32013,
            FileOpsError::UnicodeError(_) => -32014,
            FileOpsError::InvalidRequest(_) => -32600,
            FileOpsError::Internal(_) => -32603,
        };

        json!({
            "code": code,
            "message": self.to_string(),
        })
    }
}
