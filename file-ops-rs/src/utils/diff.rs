pub struct UnifiedDiff;

impl UnifiedDiff {
    pub fn generate(_original: &[String], _modified: &[String]) -> String {
        "--- original\n+++ modified\n".to_string()
    }
}
