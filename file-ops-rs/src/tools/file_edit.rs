use crate::errors::Result;

pub struct FileEditTool;

impl FileEditTool {
    pub fn new() -> Self {
        FileEditTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
