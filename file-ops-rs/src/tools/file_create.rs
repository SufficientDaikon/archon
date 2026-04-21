use crate::errors::Result;

pub struct FileCreateTool;

impl FileCreateTool {
    pub fn new() -> Self {
        FileCreateTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
