use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

pub struct Metrics {
    pub requests_total: Arc<AtomicU64>,
    pub requests_success: Arc<AtomicU64>,
    pub requests_error: Arc<AtomicU64>,
}

impl Metrics {
    pub fn new() -> Self {
        Metrics {
            requests_total: Arc::new(AtomicU64::new(0)),
            requests_success: Arc::new(AtomicU64::new(0)),
            requests_error: Arc::new(AtomicU64::new(0)),
        }
    }

    pub fn record_request(&self) {
        self.requests_total.fetch_add(1, Ordering::Relaxed);
    }

    pub fn record_success(&self) {
        self.requests_success.fetch_add(1, Ordering::Relaxed);
    }

    pub fn record_error(&self) {
        self.requests_error.fetch_add(1, Ordering::Relaxed);
    }
}

impl Clone for Metrics {
    fn clone(&self) -> Self {
        Metrics {
            requests_total: Arc::clone(&self.requests_total),
            requests_success: Arc::clone(&self.requests_success),
            requests_error: Arc::clone(&self.requests_error),
        }
    }
}
