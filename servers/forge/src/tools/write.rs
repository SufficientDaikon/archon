use rmcp::schemars::{self, JsonSchema};
use serde::Deserialize;

/// A single edit operation within a file_edit call.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct EditOp {
    /// First line to replace (1-indexed).
    pub start_line: usize,
    /// Last line to replace (inclusive).
    pub end_line: usize,
    /// Replacement content. Empty string = delete lines.
    pub content: String,
}

/// Parameters for file_edit.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileEditParams {
    /// Absolute file path.
    pub path: String,
    /// Array of edit operations.
    pub edits: Vec<EditOp>,
    /// If provided, reject if file hash doesn't match. Prevents stale edits.
    pub expected_hash: Option<String>,
    /// If true, return diff without writing to disk. Default: false.
    pub dry_run: Option<bool>,
}

/// Parameters for file_insert.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileInsertParams {
    /// Absolute file path.
    pub path: String,
    /// Insert before this line (1-indexed). Beyond EOF = append.
    pub line: usize,
    /// Content to insert (can be multi-line).
    pub content: String,
}

/// Parameters for file_delete.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileDeleteParams {
    /// Absolute file path.
    pub path: String,
    /// First line to delete (1-indexed).
    pub start_line: usize,
    /// Last line to delete (inclusive).
    pub end_line: usize,
}

/// Parameters for file_create.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileCreateParams {
    /// Absolute file path.
    pub path: String,
    /// File content.
    pub content: String,
    /// Force line ending: "lf" or "crlf". Default: "lf".
    pub line_ending: Option<String>,
}

/// Parameters for file_undo.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileUndoParams {
    /// Absolute file path.
    pub path: String,
    /// Number of operations to undo. Default: 1.
    pub steps: Option<usize>,
}

/// Parameters for file_redo.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileRedoParams {
    /// Absolute file path.
    pub path: String,
    /// Number of operations to redo. Default: 1.
    pub steps: Option<usize>,
}

/// Parameters for file_close.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct FileCloseParams {
    /// Absolute file path.
    pub path: String,
}
