use crate::errors::Result;

pub struct FileSearchTool;

impl FileSearchTool {
    pub fn new() -> Self {
        FileSearchTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
