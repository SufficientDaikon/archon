use similar::TextDiff;

/// Generate a unified diff between two strings.
/// `path` is used in the --- / +++ header lines.
pub fn unified_diff(original: &str, modified: &str, path: &str) -> String {
    let diff = TextDiff::from_lines(original, modified);
    diff.unified_diff()
        .context_radius(3)
        .header(&format!("--- {path}"), &format!("+++ {path}"))
        .to_string()
}
