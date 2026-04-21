/// file-ops-rs: High-performance Rust MCP server for file operations
///
/// Custom JSON-RPC 2.0 stdio transport with 6 core tools:
/// - file_read: Read files with range support
/// - file_edit: Atomic batch edits
/// - file_insert: Insert content
/// - file_create: Create new files
/// - file_search: Pattern matching
/// - file_structure: Language-aware outlines
///
/// Features:
/// - Custom JSON-RPC 2.0 stdio transport (no external MCP lib)
/// - Schema validation & rate limiting
/// - Structured logging & metrics
/// - Atomic writes with encoding preservation
/// - Zero-copy async/await throughout

pub mod errors;
pub mod rpc;
pub mod services;
pub mod tools;
pub mod transport;
pub mod utils;

pub use errors::{FileOpsError, Result};
