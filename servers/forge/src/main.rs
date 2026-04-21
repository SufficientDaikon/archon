mod buffer;
mod diff;
mod encoding;
mod engine;
mod errors;
mod tools;

use std::sync::Arc;
use tokio::sync::Mutex;

use rmcp::handler::server::router::tool::ToolRouter;
use rmcp::handler::server::wrapper::Parameters;
use rmcp::model::*;
use rmcp::{tool, tool_handler, tool_router, ErrorData, ServerHandler, ServiceExt};
use serde_json::json;

use engine::Engine;
use errors::ForgeError;
use tools::read::*;
use tools::write::*;

// ── Server struct ──────────────────────────────────────────────

#[derive(Clone)]
pub struct ForgeServer {
    engine: Arc<Mutex<Engine>>,
    tool_router: ToolRouter<Self>,
}

impl ForgeServer {
    pub fn new() -> Self {
        Self {
            engine: Arc::new(Mutex::new(Engine::new())),
            tool_router: Self::tool_router(),
        }
    }
}

/// Convert a ForgeError into an MCP ErrorData.
fn forge_err(e: ForgeError) -> ErrorData {
    ErrorData::new(
        rmcp::model::ErrorCode::INVALID_PARAMS,
        e.to_string(),
        Some(json!({ "code": e.code() })),
    )
}

// ── Tool implementations ───────────────────────────────────────

#[tool_router]
impl ForgeServer {
    // ─── Buffer management ─────────────────────────────────

    #[tool(description = "Open a file into a persistent buffer. Returns file metadata. \
        The file stays in memory for fast subsequent reads/edits. \
        Most other tools auto-open files, so explicit open is optional.")]
    async fn file_open(
        &self,
        Parameters(p): Parameters<FileOpenParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let buf = eng.open(&p.path).map_err(forge_err)?;
        let meta = buf.meta();
        let result = json!({
            "total_lines": meta.total_lines,
            "size_bytes": meta.size_bytes,
            "language": null,
            "encoding": meta.encoding,
            "line_ending": meta.line_ending,
            "content_hash": meta.content_hash,
            "outline": null,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&result).unwrap(),
        )]))
    }

    #[tool(description = "Close a buffer, flushing unsaved changes to disk and freeing memory. \
        No-op if file is not open.")]
    async fn file_close(
        &self,
        Parameters(p): Parameters<FileCloseParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let result = eng.close(&p.path).map_err(forge_err)?;
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&json!({
                "status": result.status,
                "flushed": result.flushed,
            }))
            .unwrap(),
        )]))
    }

    // ─── Read operations ───────────────────────────────────

    #[tool(description = "Read file content. Returns raw content EXACTLY as it exists — \
        NO line numbers, NO prefixes, NO synthetic characters injected into the content. \
        Line range metadata is in a separate field. Auto-opens the file if not already open.")]
    async fn file_read(
        &self,
        Parameters(p): Parameters<FileReadParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let result = eng
            .read(&p.path, p.start_line, p.end_line, p.max_lines)
            .map_err(forge_err)?;
        let resp = json!({
            "content": result.content,
            "lines": {
                "start": result.start,
                "end": result.end,
                "total": result.total,
            },
            "content_hash": result.content_hash,
            "truncated": result.truncated,
            "externally_modified": result.externally_modified,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Get file metadata. Auto-opens the file if not already open. \
        If file does not exist, returns exists=false with null fields.")]
    async fn file_info(
        &self,
        Parameters(p): Parameters<FileInfoParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;

        // Check existence first.
        let path = std::path::Path::new(&p.path);
        if !path.exists() {
            let resp = json!({
                "exists": false,
                "total_lines": null,
                "size_bytes": null,
                "language": null,
                "encoding": null,
                "line_ending": null,
                "is_open": false,
                "is_dirty": false,
                "content_hash": null,
            });
            return Ok(CallToolResult::success(vec![Content::text(
                serde_json::to_string_pretty(&resp).unwrap(),
            )]));
        }

        // Auto-open.
        eng.open(&p.path).map_err(forge_err)?;
        let buf = eng.get_buffer(&p.path).map_err(forge_err)?;
        let meta = buf.meta();

        let resp = json!({
            "exists": true,
            "total_lines": meta.total_lines,
            "size_bytes": meta.size_bytes,
            "language": null,
            "encoding": meta.encoding,
            "line_ending": meta.line_ending,
            "is_open": true,
            "is_dirty": meta.is_dirty,
            "content_hash": meta.content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    // ─── Write operations ──────────────────────────────────

    #[tool(description = "Apply one or more edits to a file atomically by line ranges. \
        REQUIRES file_read or file_open first. All edits succeed or none apply. \
        Edits are auto-sorted bottom-up to prevent line-shift cascades. \
        Returns a unified diff of all changes.")]
    async fn file_edit(
        &self,
        Parameters(p): Parameters<FileEditParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let mut edits: Vec<(usize, usize, String)> = p
            .edits
            .into_iter()
            .map(|e| (e.start_line, e.end_line, e.content))
            .collect();
        let dry_run = p.dry_run.unwrap_or(false);
        let expected_hash = p.expected_hash.as_deref();

        let result = eng
            .edit(&p.path, &mut edits, expected_hash, dry_run)
            .map_err(forge_err)?;

        let resp = json!({
            "diff": result.diff,
            "new_total_lines": result.new_total_lines,
            "new_content_hash": result.new_content_hash,
            "applied": result.applied,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Insert content at a specific line without replacing anything. \
        Content appears BEFORE the specified line. Use line > total_lines to append. \
        Requires file_read or file_open first.")]
    async fn file_insert(
        &self,
        Parameters(p): Parameters<FileInsertParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let result = eng.insert(&p.path, p.line, &p.content).map_err(forge_err)?;
        let resp = json!({
            "diff": result.diff,
            "new_total_lines": result.new_total_lines,
            "new_content_hash": result.new_content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Delete a range of lines from a file. \
        Requires file_read or file_open first.")]
    async fn file_delete(
        &self,
        Parameters(p): Parameters<FileDeleteParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let result = eng
            .delete(&p.path, p.start_line, p.end_line)
            .map_err(forge_err)?;
        let resp = json!({
            "diff": result.diff,
            "new_total_lines": result.new_total_lines,
            "new_content_hash": result.new_content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Create a new file. Creates parent directories if needed. \
        Fails if file already exists — use file_edit for existing files.")]
    async fn file_create(
        &self,
        Parameters(p): Parameters<FileCreateParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let result = eng
            .create(&p.path, &p.content, p.line_ending.as_deref())
            .map_err(forge_err)?;
        let resp = json!({
            "total_lines": result.total_lines,
            "size_bytes": result.size_bytes,
            "content_hash": result.content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Undo the last write operation(s) on a file. \
        Returns a combined diff and descriptions of undone operations. \
        Redo becomes available after undo.")]
    async fn file_undo(
        &self,
        Parameters(p): Parameters<FileUndoParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let steps = p.steps.unwrap_or(1);
        let result = eng.undo(&p.path, steps).map_err(forge_err)?;
        let resp = json!({
            "diff": result.diff,
            "descriptions": result.descriptions,
            "remaining_undos": result.remaining_undos,
            "remaining_redos": result.remaining_redos,
            "new_content_hash": result.new_content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }

    #[tool(description = "Redo the last undone operation(s). Only available after file_undo. \
        Any new write operation clears the redo stack.")]
    async fn file_redo(
        &self,
        Parameters(p): Parameters<FileRedoParams>,
    ) -> Result<CallToolResult, ErrorData> {
        let mut eng = self.engine.lock().await;
        let steps = p.steps.unwrap_or(1);
        let result = eng.redo(&p.path, steps).map_err(forge_err)?;
        let resp = json!({
            "diff": result.diff,
            "descriptions": result.descriptions,
            "remaining_undos": result.remaining_undos,
            "remaining_redos": result.remaining_redos,
            "new_content_hash": result.new_content_hash,
        });
        Ok(CallToolResult::success(vec![Content::text(
            serde_json::to_string_pretty(&resp).unwrap(),
        )]))
    }
}

// ── ServerHandler trait ────────────────────────────────────────

#[tool_handler]
impl ServerHandler for ForgeServer {
    fn get_info(&self) -> ServerInfo {
        let instructions = "\
FORGE provides reliable file operations using LINE NUMBERS instead of string matching.

PREFER these tools over built-in Read/Edit/Write for all file operations:
- file_read: Read files — raw content, NO baked-in line numbers
- file_edit: Edit by line ranges — atomic, batch, with diff output
- file_create: Create new files with parent dir creation
- file_insert: Insert content at a specific line
- file_delete: Delete a range of lines
- file_undo/file_redo: Undo/redo any write operation

Typical workflow: file_read → file_edit → file_read (verify)

Fall back to built-in Read for: images, PDFs, notebooks (.ipynb)
Fall back to built-in Write for: binary files";

        ServerInfo::new(
            ServerCapabilities::builder().enable_tools().build(),
        ).with_instructions(instructions)
    }
}

// ── Entry point ────────────────────────────────────────────────

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Log to stderr — stdout is reserved for MCP JSON-RPC.
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_ansi(false)
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("forge=info".parse().unwrap()),
        )
        .init();

    tracing::info!("FORGE v{} starting on stdio", env!("CARGO_PKG_VERSION"));

    let server = ForgeServer::new();
    let service = server.serve(rmcp::transport::stdio()).await?;
    service.waiting().await?;

    tracing::info!("FORGE shutting down");
    Ok(())
}
