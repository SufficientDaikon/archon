pub struct Validation;

impl Validation {
    pub fn validate_params(_params: &serde_json::Value, _schema: &serde_json::Value) -> crate::errors::Result<()> {
        Ok(())
    }
}
