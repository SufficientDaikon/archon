pub struct LanguageParser;

impl LanguageParser {
    pub fn parse_python(_lines: &[String]) -> serde_json::Value {
        serde_json::json!({"outline": []})
    }
}
