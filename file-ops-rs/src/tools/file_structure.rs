use crate::errors::Result;

pub struct FileStructureTool;

impl FileStructureTool {
    pub fn new() -> Self {
        FileStructureTool
    }

    pub async fn call(&self, _params: serde_json::Value) -> Result<serde_json::Value> {
        Ok(serde_json::json!({"status": "not implemented"}))
    }
}
