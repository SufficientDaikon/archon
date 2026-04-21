use crate::transport::{JsonRpcRequest, JsonRpcResponse};

pub struct RpcRouter;

impl RpcRouter {
    pub fn new() -> Self {
        RpcRouter
    }

    pub async fn dispatch(&self, request: JsonRpcRequest) -> JsonRpcResponse {
        JsonRpcResponse::method_not_found(&request.method)
    }
}
