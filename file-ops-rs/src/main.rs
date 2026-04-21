/// Entry point for file-ops-rs MCP server
use file_ops_rs::transport::StdioTransport;
use file_ops_rs::services;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Setup logging
    services::logging::setup_logging();

    eprintln!("[file-ops-rs] Starting MCP server");

    // Create stdio transport
    let transport = StdioTransport::new();

    // Initialize metrics
    let metrics = services::Metrics::new();

    // Initialize rate limiter
    let rate_limiter = services::RateLimiter::new();

    eprintln!("[file-ops-rs] Services initialized");
    eprintln!("[file-ops-rs] Ready to handle requests");

    // Main request loop
    loop {
        match transport.read_request().await {
            Ok(request) => {
                metrics.record_request();

                // For now, just return method not found
                let response =
                    file_ops_rs::transport::JsonRpcResponse::method_not_found(&request.method);

                if let Err(e) = transport.send_response(response).await {
                    eprintln!("[ERROR] Failed to send response: {}", e);
                }
            }
            Err(e) => {
                eprintln!("[ERROR] Failed to read request: {}", e);
                // On stdin EOF, exit gracefully
                break;
            }
        }
    }

    eprintln!("[file-ops-rs] Server shutdown");
    Ok(())
}
