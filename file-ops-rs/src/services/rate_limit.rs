pub struct RateLimiter;

impl RateLimiter {
    pub fn new() -> Self {
        RateLimiter
    }

    pub fn check_rate(&self, _request: &crate::transport::JsonRpcRequest) -> crate::errors::Result<()> {
        Ok(())
    }
}
