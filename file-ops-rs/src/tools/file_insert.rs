use crate::errors::Result;

pub struct FileInsertTool;

impl FileInsertTool {
    pub fn new() -> Self {
        FileInsertTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
