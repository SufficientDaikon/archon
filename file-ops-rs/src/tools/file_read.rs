use crate::errors::Result;

pub struct FileReadTool;

impl FileReadTool {
    pub fn new() -> Self {
        FileReadTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
