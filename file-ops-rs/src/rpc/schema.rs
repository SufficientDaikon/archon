pub struct SchemaValidator;

impl SchemaValidator {
    pub fn validate_request(_request: &crate::transport::JsonRpcRequest) -> crate::errors::Result<()> {
        Ok(())
    }
}
