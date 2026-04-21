use std::collections::HashMap;
use std::path::PathBuf;

use crate::buffer::Buffer;
use crate::encoding::{normalize_to_lf, LineEnding};
use crate::errors::{ForgeError, ForgeResult};

/// Central coordinator for all file buffers.
pub struct Engine {
    pub buffers: HashMap<PathBuf, Buffer>,
}

impl Engine {
    pub fn new() -> Self {
        Self {
            buffers: HashMap::new(),
        }
    }

    /// Canonicalize a path for consistent buffer lookup.
    fn normalize_path(path: &str) -> ForgeResult<PathBuf> {
        let p = PathBuf::from(path);
        // On Windows, normalize forward slashes and try to canonicalize.
        match std::fs::canonicalize(&p) {
            Ok(canonical) => Ok(canonical),
            Err(_) => {
                // File might not exist yet (file_create). Return as-is.
                Ok(p)
            }
        }
    }

    /// Open a file into a buffer. If already open, returns the existing buffer.
    pub fn open(&mut self, path: &str) -> ForgeResult<&Buffer> {
        let norm = Self::normalize_path(path)?;
        if !self.buffers.contains_key(&norm) {
            let buf = Buffer::open(&norm)?;
            self.buffers.insert(norm.clone(), buf);
        }
        Ok(self.buffers.get(&norm).unwrap())
    }

    /// Get a reference to an open buffer, or error.
    pub fn get_buffer(&self, path: &str) -> ForgeResult<&Buffer> {
        let norm = Self::normalize_path(path)?;
        self.buffers
            .get(&norm)
            .ok_or_else(|| ForgeError::FileNotOpen(format!(
                "{path} — call file_read or file_open first"
            )))
    }

    /// Get a mutable reference to an open buffer, or error.
    pub fn get_buffer_mut(&mut self, path: &str) -> ForgeResult<&mut Buffer> {
        let norm = Self::normalize_path(path)?;
        self.buffers
            .get_mut(&norm)
            .ok_or_else(|| ForgeError::FileNotOpen(format!(
                "{path} — call file_read or file_open first"
            )))
    }

    /// Check if a file is currently open.
    pub fn is_open(&self, path: &str) -> bool {
        Self::normalize_path(path)
            .map(|norm| self.buffers.contains_key(&norm))
            .unwrap_or(false)
    }

    /// Open + read a file. Auto-opens if not already open.
    pub fn read(
        &mut self,
        path: &str,
        start_line: Option<usize>,
        end_line: Option<usize>,
        max_lines: Option<usize>,
    ) -> ForgeResult<ReadResult> {
        // Auto-open.
        self.open(path)?;
        let buf = self.get_buffer(path)?;

        let total = buf.rope.len_lines();
        let start = start_line.unwrap_or(1);
        let max = max_lines.unwrap_or(500).min(5000);
        let mut end = end_line.unwrap_or(total);

        // Apply max_lines cap.
        let truncated = (end - start + 1) > max;
        if truncated {
            end = start + max - 1;
        }
        let end = end.min(total);

        let content = buf.read_range(start, end)?;

        Ok(ReadResult {
            content,
            start,
            end,
            total,
            content_hash: format!("{:016x}", buf.content_hash),
            truncated,
            externally_modified: buf.externally_modified,
        })
    }

    /// Apply edits to a file. File must already be open.
    pub fn edit(
        &mut self,
        path: &str,
        edits: &mut [(usize, usize, String)],
        expected_hash: Option<&str>,
        dry_run: bool,
    ) -> ForgeResult<EditResult> {
        let buf = self.get_buffer_mut(path)?;

        if dry_run {
            // Clone the rope, apply edits on clone, return diff without modifying.
            let mut clone = Buffer {
                path: buf.path.clone(),
                rope: buf.rope.clone(),
                encoding: buf.encoding,
                line_ending: buf.line_ending,
                content_hash: buf.content_hash,
                disk_hash: buf.disk_hash,
                undo_stack: Vec::new(),
                redo_stack: Vec::new(),
                dirty: false,
                last_modified: buf.last_modified,
                externally_modified: buf.externally_modified,
            };
            let diff = clone.apply_edits(edits, expected_hash)?;
            return Ok(EditResult {
                diff,
                new_total_lines: clone.rope.len_lines(),
                new_content_hash: format!("{:016x}", clone.content_hash),
                applied: false,
            });
        }

        let diff = buf.apply_edits(edits, expected_hash)?;
        let new_total = buf.rope.len_lines();
        let new_hash = format!("{:016x}", buf.content_hash);
        buf.flush()?;

        Ok(EditResult {
            diff,
            new_total_lines: new_total,
            new_content_hash: new_hash,
            applied: true,
        })
    }

    /// Insert content at a line. File must already be open.
    pub fn insert(&mut self, path: &str, line: usize, content: &str) -> ForgeResult<EditResult> {
        let buf = self.get_buffer_mut(path)?;
        let diff = buf.insert_at(line, content)?;
        let new_total = buf.rope.len_lines();
        let new_hash = format!("{:016x}", buf.content_hash);
        buf.flush()?;

        Ok(EditResult {
            diff,
            new_total_lines: new_total,
            new_content_hash: new_hash,
            applied: true,
        })
    }

    /// Delete a line range. File must already be open.
    pub fn delete(&mut self, path: &str, start: usize, end: usize) -> ForgeResult<EditResult> {
        let buf = self.get_buffer_mut(path)?;
        let diff = buf.delete_range(start, end)?;
        let new_total = buf.rope.len_lines();
        let new_hash = format!("{:016x}", buf.content_hash);
        buf.flush()?;

        Ok(EditResult {
            diff,
            new_total_lines: new_total,
            new_content_hash: new_hash,
            applied: true,
        })
    }

    /// Create a new file. Fails if the file already exists.
    pub fn create(
        &mut self,
        path: &str,
        content: &str,
        line_ending: Option<&str>,
    ) -> ForgeResult<CreateResult> {
        let p = PathBuf::from(path);
        if p.exists() {
            return Err(ForgeError::FileExists(format!(
                "{path} already exists. Use file_edit for modifications."
            )));
        }

        // Create parent directories.
        if let Some(parent) = p.parent() {
            std::fs::create_dir_all(parent)?;
        }

        let ending = match line_ending {
            Some("crlf") => LineEnding::Crlf,
            _ => LineEnding::Lf,
        };

        let normalized = normalize_to_lf(content);
        let disk_content = crate::encoding::apply_line_ending(&normalized, ending);
        std::fs::write(&p, disk_content.as_bytes())?;

        // Open into buffer.
        let buf = Buffer::open(&p)?;
        let meta = buf.meta();
        let norm = Self::normalize_path(path)?;
        self.buffers.insert(norm, buf);

        Ok(CreateResult {
            total_lines: meta.total_lines,
            size_bytes: meta.size_bytes,
            content_hash: meta.content_hash,
        })
    }

    /// Undo last N operations on a file.
    pub fn undo(&mut self, path: &str, steps: usize) -> ForgeResult<UndoResult> {
        let buf = self.get_buffer_mut(path)?;
        let (diff, descriptions) = buf.undo(steps)?;
        let remaining_undos = buf.undo_stack.len();
        let remaining_redos = buf.redo_stack.len();
        let new_hash = format!("{:016x}", buf.content_hash);
        buf.flush()?;

        Ok(UndoResult {
            diff,
            descriptions,
            remaining_undos,
            remaining_redos,
            new_content_hash: new_hash,
        })
    }

    /// Redo last N undone operations on a file.
    pub fn redo(&mut self, path: &str, steps: usize) -> ForgeResult<UndoResult> {
        let buf = self.get_buffer_mut(path)?;
        let (diff, descriptions) = buf.redo(steps)?;
        let remaining_undos = buf.undo_stack.len();
        let remaining_redos = buf.redo_stack.len();
        let new_hash = format!("{:016x}", buf.content_hash);
        buf.flush()?;

        Ok(UndoResult {
            diff,
            descriptions,
            remaining_undos,
            remaining_redos,
            new_content_hash: new_hash,
        })
    }

    /// Close a buffer, flushing if dirty.
    pub fn close(&mut self, path: &str) -> ForgeResult<CloseResult> {
        let norm = Self::normalize_path(path)?;
        match self.buffers.remove(&norm) {
            Some(mut buf) => {
                let flushed = buf.dirty;
                if flushed {
                    buf.flush()?;
                }
                Ok(CloseResult {
                    status: "closed".to_string(),
                    flushed,
                })
            }
            None => Ok(CloseResult {
                status: "not_open".to_string(),
                flushed: false,
            }),
        }
    }
}

// ── Result types ────────────────────────────────────────────────

#[derive(Debug, serde::Serialize)]
pub struct ReadResult {
    pub content: String,
    pub start: usize,
    pub end: usize,
    pub total: usize,
    pub content_hash: String,
    pub truncated: bool,
    pub externally_modified: bool,
}

#[derive(Debug, serde::Serialize)]
pub struct EditResult {
    pub diff: String,
    pub new_total_lines: usize,
    pub new_content_hash: String,
    pub applied: bool,
}

#[derive(Debug, serde::Serialize)]
pub struct CreateResult {
    pub total_lines: usize,
    pub size_bytes: u64,
    pub content_hash: String,
}

#[derive(Debug, serde::Serialize)]
pub struct UndoResult {
    pub diff: String,
    pub descriptions: Vec<String>,
    pub remaining_undos: usize,
    pub remaining_redos: usize,
    pub new_content_hash: String,
}

#[derive(Debug, serde::Serialize)]
pub struct CloseResult {
    pub status: String,
    pub flushed: bool,
}
