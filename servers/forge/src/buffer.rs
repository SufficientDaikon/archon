use std::path::{Path, PathBuf};
use std::time::SystemTime;

use ropey::Rope;
use serde::Serialize;
use xxhash_rust::xxh64::xxh64;

use crate::encoding::{
    apply_line_ending, detect_line_ending, normalize_to_lf, read_file_bytes, Encoding, LineEnding,
};
use crate::errors::{ForgeError, ForgeResult};

/// A snapshot for undo/redo.
#[derive(Clone)]
pub struct UndoEntry {
    pub rope: Rope,
    pub description: String,
}

/// An in-memory file buffer backed by a rope.
pub struct Buffer {
    pub path: PathBuf,
    pub rope: Rope,
    pub encoding: Encoding,
    pub line_ending: LineEnding,
    pub content_hash: u64,
    pub disk_hash: u64,
    pub undo_stack: Vec<UndoEntry>,
    pub redo_stack: Vec<UndoEntry>,
    pub dirty: bool,
    pub last_modified: Option<SystemTime>,
    pub externally_modified: bool,
}

/// Metadata returned by read operations.
#[derive(Debug, Serialize)]
pub struct BufferMeta {
    pub total_lines: usize,
    pub size_bytes: u64,
    pub encoding: Encoding,
    pub line_ending: LineEnding,
    pub content_hash: String,
    pub is_dirty: bool,
}

impl Buffer {
    /// Open a file from disk into a buffer.
    pub fn open(path: &Path) -> ForgeResult<Self> {
        let (content, encoding, _raw) = read_file_bytes(path)?;
        let line_ending = detect_line_ending(&content);
        let normalized = normalize_to_lf(&content);
        let rope = Rope::from_str(&normalized);
        let hash = xxh64(normalized.as_bytes(), 0);

        let mtime = std::fs::metadata(path).ok().and_then(|m| m.modified().ok());

        Ok(Self {
            path: path.to_path_buf(),
            rope,
            encoding,
            line_ending,
            content_hash: hash,
            disk_hash: hash,
            undo_stack: Vec::new(),
            redo_stack: Vec::new(),
            dirty: false,
            last_modified: mtime,
            externally_modified: false,
        })
    }

    /// Get metadata about this buffer.
    pub fn meta(&self) -> BufferMeta {
        let size = self.rope.len_bytes() as u64;
        BufferMeta {
            total_lines: self.rope.len_lines(),
            size_bytes: size,
            encoding: self.encoding,
            line_ending: self.line_ending,
            content_hash: format!("{:016x}", self.content_hash),
            is_dirty: self.dirty,
        }
    }

    /// Get the full content as a string (LF-normalized, as stored in rope).
    pub fn content(&self) -> String {
        self.rope.to_string()
    }

    /// Read a line range (1-indexed, inclusive). Returns raw content — no line numbers.
    pub fn read_range(&self, start: usize, end: usize) -> ForgeResult<String> {
        let total = self.rope.len_lines();
        // Handle edge case: empty file has 1 "line" in ropey but no content.
        if total == 0 || (total == 1 && self.rope.len_chars() == 0) {
            if start > 1 {
                return Err(ForgeError::LineOutOfRange(format!(
                    "start_line {start} exceeds file length (0 lines)"
                )));
            }
            return Ok(String::new());
        }

        if start < 1 || start > total {
            return Err(ForgeError::LineOutOfRange(format!(
                "start_line {start} out of range (file has {total} lines)"
            )));
        }
        let clamped_end = end.min(total);
        if clamped_end < start {
            return Err(ForgeError::LineOutOfRange(format!(
                "end_line {end} is before start_line {start}"
            )));
        }

        let start_idx = start - 1; // 0-indexed
        let mut result = String::new();
        for i in start_idx..clamped_end {
            let line = self.rope.line(i);
            result.push_str(&line.to_string());
        }
        Ok(result)
    }

    /// Push current state onto undo stack before a mutation.
    fn push_undo(&mut self, description: String) {
        self.undo_stack.push(UndoEntry {
            rope: self.rope.clone(), // Cheap: ropey uses COW
            description,
        });
        // Any new edit clears the redo stack.
        self.redo_stack.clear();
    }

    /// Apply a single edit: replace lines start..=end with content.
    /// Lines are 1-indexed, inclusive. content may be empty (deletion).
    /// Does NOT flush to disk — caller must call flush() after all edits.
    fn apply_single_edit(&mut self, start: usize, end: usize, content: &str) -> ForgeResult<()> {
        let total = self.rope.len_lines();

        if start < 1 {
            return Err(ForgeError::LineOutOfRange(
                "start_line must be >= 1".to_string(),
            ));
        }
        if end < start {
            return Err(ForgeError::LineOutOfRange(format!(
                "end_line {end} < start_line {start}"
            )));
        }
        if start > total {
            return Err(ForgeError::LineOutOfRange(format!(
                "start_line {start} exceeds file length ({total} lines)"
            )));
        }
        if end > total {
            return Err(ForgeError::LineOutOfRange(format!(
                "end_line {end} exceeds file length ({total} lines)"
            )));
        }

        // Convert to char indices for ropey.
        let start_char = self.rope.line_to_char(start - 1);
        let end_char = if end >= total {
            self.rope.len_chars()
        } else {
            self.rope.line_to_char(end)
        };

        // Build replacement content with proper trailing newline.
        let mut replacement = content.to_string();
        if !content.is_empty() && !content.ends_with('\n') && end < total {
            replacement.push('\n');
        }

        self.rope.remove(start_char..end_char);
        if !replacement.is_empty() {
            self.rope.insert(start_char, &replacement);
        }

        Ok(())
    }

    /// Apply multiple edits atomically. Edits are sorted bottom-up.
    /// Returns the diff between original and modified content.
    pub fn apply_edits(
        &mut self,
        edits: &mut [(usize, usize, String)],
        expected_hash: Option<&str>,
    ) -> ForgeResult<String> {
        // Hash check.
        if let Some(expected) = expected_hash {
            let current = format!("{:016x}", self.content_hash);
            if current != expected {
                return Err(ForgeError::HashMismatch(format!(
                    "expected {expected}, current {current}. File was modified since last read."
                )));
            }
        }

        // Validate: no overlapping ranges.
        edits.sort_by(|a, b| a.0.cmp(&b.0));
        for pair in edits.windows(2) {
            if pair[0].1 >= pair[1].0 {
                return Err(ForgeError::OverlappingRanges(format!(
                    "edit [{}-{}] overlaps with [{}-{}]",
                    pair[0].0, pair[0].1, pair[1].0, pair[1].1
                )));
            }
        }

        let original = self.content();

        // Build description.
        let desc = if edits.len() == 1 {
            format!("edit lines {}-{}", edits[0].0, edits[0].1)
        } else {
            format!("batch edit ({} regions)", edits.len())
        };
        self.push_undo(desc);

        // Apply bottom-up (reverse order by start_line) to avoid line shift cascades.
        edits.sort_by(|a, b| b.0.cmp(&a.0));
        for (start, end, content) in edits.iter() {
            self.apply_single_edit(*start, *end, content)?;
        }

        self.update_hash();
        self.dirty = true;

        let modified = self.content();
        let diff = crate::diff::unified_diff(&original, &modified, &self.path.display().to_string());
        Ok(diff)
    }

    /// Insert content before a given line (1-indexed). line > total appends.
    pub fn insert_at(&mut self, line: usize, content: &str) -> ForgeResult<String> {
        let original = self.content();
        let total = self.rope.len_lines();

        self.push_undo(format!("insert at line {line}"));

        let mut text = content.to_string();
        if !text.ends_with('\n') {
            text.push('\n');
        }

        if line > total {
            // Append at end.
            let end = self.rope.len_chars();
            // Ensure there's a trailing newline before appending.
            if end > 0 {
                let last_char = self.rope.char(end - 1);
                if last_char != '\n' {
                    self.rope.insert(end, "\n");
                }
            }
            let end = self.rope.len_chars();
            self.rope.insert(end, &text);
        } else if line < 1 {
            return Err(ForgeError::LineOutOfRange(
                "line must be >= 1".to_string(),
            ));
        } else {
            let char_idx = self.rope.line_to_char(line - 1);
            self.rope.insert(char_idx, &text);
        }

        self.update_hash();
        self.dirty = true;

        let modified = self.content();
        Ok(crate::diff::unified_diff(&original, &modified, &self.path.display().to_string()))
    }

    /// Delete a range of lines (1-indexed, inclusive).
    pub fn delete_range(&mut self, start: usize, end: usize) -> ForgeResult<String> {
        // Implemented as an edit that replaces the range with empty string.
        let mut edits = vec![(start, end, String::new())];
        // Override the undo description.
        let original = self.content();
        self.push_undo(format!("delete lines {start}-{end}"));

        // Apply directly (no double push_undo — apply_single_edit doesn't push).
        edits.sort_by(|a, b| b.0.cmp(&a.0));
        for (s, e, c) in &edits {
            self.apply_single_edit(*s, *e, c)?;
        }

        self.update_hash();
        self.dirty = true;

        let modified = self.content();
        Ok(crate::diff::unified_diff(&original, &modified, &self.path.display().to_string()))
    }

    /// Undo the last N operations. Returns combined diff and descriptions.
    pub fn undo(&mut self, steps: usize) -> ForgeResult<(String, Vec<String>)> {
        if self.undo_stack.is_empty() {
            return Err(ForgeError::NothingToUndo("no undo history".to_string()));
        }
        if steps > self.undo_stack.len() {
            return Err(ForgeError::InsufficientHistory(format!(
                "requested {steps} undos but only {} available",
                self.undo_stack.len()
            )));
        }

        let original = self.content();
        let mut descriptions = Vec::new();

        for _ in 0..steps {
            let entry = self.undo_stack.pop().unwrap();
            descriptions.push(entry.description.clone());
            // Push current state to redo.
            self.redo_stack.push(UndoEntry {
                rope: self.rope.clone(),
                description: entry.description,
            });
            self.rope = entry.rope;
        }

        self.update_hash();
        self.dirty = true;

        let modified = self.content();
        let diff = crate::diff::unified_diff(&original, &modified, &self.path.display().to_string());
        Ok((diff, descriptions))
    }

    /// Redo the last N undone operations. Returns combined diff and descriptions.
    pub fn redo(&mut self, steps: usize) -> ForgeResult<(String, Vec<String>)> {
        if self.redo_stack.is_empty() {
            return Err(ForgeError::NothingToRedo(
                "no redo history (any new write clears the redo stack)".to_string(),
            ));
        }
        if steps > self.redo_stack.len() {
            return Err(ForgeError::InsufficientHistory(format!(
                "requested {steps} redos but only {} available",
                self.redo_stack.len()
            )));
        }

        let original = self.content();
        let mut descriptions = Vec::new();

        for _ in 0..steps {
            let entry = self.redo_stack.pop().unwrap();
            descriptions.push(entry.description.clone());
            self.undo_stack.push(UndoEntry {
                rope: self.rope.clone(),
                description: entry.description,
            });
            self.rope = entry.rope;
        }

        // Redo descriptions should be oldest-first.
        descriptions.reverse();

        self.update_hash();
        self.dirty = true;

        let modified = self.content();
        let diff = crate::diff::unified_diff(&original, &modified, &self.path.display().to_string());
        Ok((diff, descriptions))
    }

    /// Flush buffer to disk atomically (tempfile + rename).
    pub fn flush(&mut self) -> ForgeResult<()> {
        if !self.dirty {
            return Ok(());
        }

        let content = self.content();
        let disk_content = apply_line_ending(&content, self.line_ending);

        let parent = self.path.parent().unwrap_or(Path::new("."));
        let mut tmp = tempfile::NamedTempFile::new_in(parent)?;
        std::io::Write::write_all(&mut tmp, disk_content.as_bytes())?;
        tmp.persist(&self.path).map_err(|e| {
            ForgeError::Internal(format!("atomic rename failed: {e}"))
        })?;

        self.disk_hash = self.content_hash;
        self.dirty = false;
        self.last_modified = std::fs::metadata(&self.path)
            .ok()
            .and_then(|m| m.modified().ok());

        Ok(())
    }

    /// Recalculate content hash from the rope.
    fn update_hash(&mut self) {
        let content = self.rope.to_string();
        self.content_hash = xxh64(content.as_bytes(), 0);
    }
}
