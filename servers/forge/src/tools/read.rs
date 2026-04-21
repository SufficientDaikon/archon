use rmcp::schemars::{self, JsonSchema};
use serde::Deserialize;

/// Parameters for file_open.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileOpenParams {
    /// Absolute file path.
    pub path: String,
}

/// Parameters for file_read.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileReadParams {
    /// Absolute file path.
    pub path: String,
    /// First line to read (1-indexed). Default: 1.
    pub start_line: Option<usize>,
    /// Last line to read (inclusive). Default: last line of file.
    pub end_line: Option<usize>,
    /// Maximum lines to return. Default: 500. Max: 5000.
    pub max_lines: Option<usize>,
}

/// Parameters for file_info.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileInfoParams {
    /// Absolute file path.
    pub path: String,
}
