use std::path::Path;

use crate::errors::{ForgeError, ForgeResult};

/// Detected line ending style.
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize)]
#[serde(rename_all = "lowercase")]
pub enum LineEnding {
    Lf,
    Crlf,
    Mixed,
}

impl LineEnding {
    /// The string to use when constructing new lines.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Lf | Self::Mixed => "\n",
            Self::Crlf => "\r\n",
        }
    }
}

/// Detected file encoding.
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum Encoding {
    Utf8,
    Latin1,
}

/// Check if raw bytes look like a binary file (null bytes in first 8KB).
pub fn is_binary(bytes: &[u8]) -> bool {
    let check_len = bytes.len().min(8192);
    bytes[..check_len].contains(&0)
}

/// Detect line ending style from raw bytes.
pub fn detect_line_ending(content: &str) -> LineEnding {
    let has_crlf = content.contains("\r\n");
    // Check for bare LF (not preceded by CR).
    let has_bare_lf = content.bytes().enumerate().any(|(i, b)| {
        b == b'\n' && (i == 0 || content.as_bytes()[i - 1] != b'\r')
    });

    match (has_crlf, has_bare_lf) {
        (true, true) => LineEnding::Mixed,
        (true, false) => LineEnding::Crlf,
        _ => LineEnding::Lf,
    }
}

/// Read a file from disk, detecting encoding. Returns (decoded content, encoding, raw bytes).
pub fn read_file_bytes(path: &Path) -> ForgeResult<(String, Encoding, Vec<u8>)> {
    let raw = std::fs::read(path).map_err(|e| {
        if e.kind() == std::io::ErrorKind::NotFound {
            ForgeError::FileNotFound(path.display().to_string())
        } else if e.kind() == std::io::ErrorKind::PermissionDenied {
            ForgeError::PermissionDenied(path.display().to_string())
        } else {
            ForgeError::Io(e)
        }
    })?;

    if is_binary(&raw) {
        return Err(ForgeError::BinaryFile(path.display().to_string()));
    }

    // Try UTF-8 first.
    match std::str::from_utf8(&raw) {
        Ok(s) => Ok((s.to_string(), Encoding::Utf8, raw)),
        Err(_) => {
            // Fallback to Latin-1 (ISO-8859-1) — every byte is valid.
            let (decoded, _, _) = encoding_rs::WINDOWS_1252.decode(&raw);
            Ok((decoded.into_owned(), Encoding::Latin1, raw))
        }
    }
}

/// Normalize content for the rope: convert all line endings to LF internally.
/// The original line ending style is preserved in metadata and re-applied on flush.
pub fn normalize_to_lf(content: &str) -> String {
    content.replace("\r\n", "\n")
}

/// Convert LF content back to the target line ending for writing to disk.
pub fn apply_line_ending(content: &str, ending: LineEnding) -> String {
    match ending {
        LineEnding::Lf | LineEnding::Mixed => content.to_string(),
        LineEnding::Crlf => content.replace('\n', "\r\n"),
    }
}
