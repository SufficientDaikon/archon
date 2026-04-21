use thiserror::Error;

/// All FORGE error codes, mapped to MCP tool error responses.
#[derive(Debug, Error)]
pub enum ForgeError {
    #[error("FILE_NOT_FOUND: {0}")]
    FileNotFound(String),

    #[error("BINARY_FILE: {0}")]
    BinaryFile(String),

    #[error("PERMISSION_DENIED: {0}")]
    PermissionDenied(String),

    #[error("LINE_OUT_OF_RANGE: {0}")]
    LineOutOfRange(String),

    #[error("FILE_NOT_OPEN: {0}")]
    FileNotOpen(String),

    #[error("FILE_EXISTS: {0}")]
    FileExists(String),

    #[error("HASH_MISMATCH: {0}")]
    HashMismatch(String),

    #[error("OVERLAPPING_RANGES: {0}")]
    OverlappingRanges(String),

    #[error("NOTHING_TO_UNDO: {0}")]
    NothingToUndo(String),

    #[error("NOTHING_TO_REDO: {0}")]
    NothingToRedo(String),

    #[error("INSUFFICIENT_HISTORY: {0}")]
    InsufficientHistory(String),

    #[error("IO_ERROR: {0}")]
    Io(#[from] std::io::Error),

    #[error("INTERNAL: {0}")]
    Internal(String),
}

impl ForgeError {
    /// Extract the error code prefix (e.g. "FILE_NOT_FOUND").
    pub fn code(&self) -> &'static str {
        match self {
            Self::FileNotFound(_) => "FILE_NOT_FOUND",
            Self::BinaryFile(_) => "BINARY_FILE",
            Self::PermissionDenied(_) => "PERMISSION_DENIED",
            Self::LineOutOfRange(_) => "LINE_OUT_OF_RANGE",
            Self::FileNotOpen(_) => "FILE_NOT_OPEN",
            Self::FileExists(_) => "FILE_EXISTS",
            Self::HashMismatch(_) => "HASH_MISMATCH",
            Self::OverlappingRanges(_) => "OVERLAPPING_RANGES",
            Self::NothingToUndo(_) => "NOTHING_TO_UNDO",
            Self::NothingToRedo(_) => "NOTHING_TO_REDO",
            Self::InsufficientHistory(_) => "INSUFFICIENT_HISTORY",
            Self::Io(_) => "IO_ERROR",
            Self::Internal(_) => "INTERNAL",
        }
    }
}

pub type ForgeResult<T> = Result<T, ForgeError>;
