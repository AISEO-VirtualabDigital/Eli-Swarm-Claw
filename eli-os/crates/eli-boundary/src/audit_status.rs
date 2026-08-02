use crate::{BoundaryAuditReport, BoundaryAuditReportVerdict};

/// Compact read-only status projection for a boundary audit report.
///
/// This is a reporting view only. It does not persist data, emit logs,
/// expose HTTP, call Python, route work, or execute tasks.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BoundaryAuditStatusView {
    verdict: BoundaryAuditReportVerdict,
    verdict_label: String,
    total_count: usize,
    accepted_count: usize,
    rejected_count: usize,
    latest_processed_at_unix_ms: Option<u64>,
}

impl BoundaryAuditStatusView {
    #[must_use]
    pub fn from_report(report: &BoundaryAuditReport) -> Self {
        let verdict = report.verdict();

        Self {
            verdict_label: verdict_label(&verdict).to_owned(),
            verdict,
            total_count: report.total_count(),
            accepted_count: report.accepted_count(),
            rejected_count: report.rejected_count(),
            latest_processed_at_unix_ms: report.latest_processed_at_unix_ms(),
        }
    }

    #[must_use]
    pub fn verdict(&self) -> &BoundaryAuditReportVerdict {
        &self.verdict
    }

    #[must_use]
    pub fn verdict_label(&self) -> &str {
        &self.verdict_label
    }

    #[must_use]
    pub fn total_count(&self) -> usize {
        self.total_count
    }

    #[must_use]
    pub fn accepted_count(&self) -> usize {
        self.accepted_count
    }

    #[must_use]
    pub fn rejected_count(&self) -> usize {
        self.rejected_count
    }

    #[must_use]
    pub fn latest_processed_at_unix_ms(&self) -> Option<u64> {
        self.latest_processed_at_unix_ms
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.verdict == BoundaryAuditReportVerdict::Empty
    }

    #[must_use]
    pub fn has_rejections(&self) -> bool {
        self.verdict == BoundaryAuditReportVerdict::ContainsRejections
    }
}

fn verdict_label(verdict: &BoundaryAuditReportVerdict) -> &'static str {
    match verdict {
        BoundaryAuditReportVerdict::Empty => "empty",
        BoundaryAuditReportVerdict::AcceptedOnly => "accepted_only",
        BoundaryAuditReportVerdict::ContainsRejections => "contains_rejections",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        AuthenticatedBoundaryEnvelope, AuthenticationKey, BoundaryAuditEvent,
        BoundaryDecisionReceipt, BoundaryEnvelope, BoundaryError, BoundaryErrorCode,
        BoundaryOperation, CorrelationId, GenerationRequest, IdempotencyKey, KeyId,
        PythonBoundaryRequest,
    };
    use eli_core::AgentTaskAnchorId;

    fn authentication_key() -> AuthenticationKey {
        AuthenticationKey::new(b"0123456789abcdef0123456789abcdef".to_vec())
            .expect("valid authentication key")
    }

    fn key_id(value: &str) -> KeyId {
        KeyId::new(value).expect("valid key ID")
    }

    fn boundary_request() -> PythonBoundaryRequest {
        PythonBoundaryRequest::generation(
            AgentTaskAnchorId::new(),
            Some(101),
            Some(42),
            BoundaryOperation::GenerateImage,
            GenerationRequest::with_python_defaults("Create image"),
        )
    }

    fn boundary_envelope(correlation_id: &str, idempotency_key: &str) -> BoundaryEnvelope {
        BoundaryEnvelope::new(
            CorrelationId::new(correlation_id),
            IdempotencyKey::new(idempotency_key),
            1_000,
            5_000,
            boundary_request(),
        )
    }

    fn accepted_event(
        correlation_id: &str,
        idempotency_key: &str,
        processed_at_unix_ms: u64,
    ) -> BoundaryAuditEvent {
        let envelope = boundary_envelope(correlation_id, idempotency_key);
        let receipt = BoundaryDecisionReceipt::from_envelope(
            &envelope,
            key_id("active-key"),
            processed_at_unix_ms,
        );

        BoundaryAuditEvent::from_parts(&receipt, &envelope.request)
    }

    fn rejected_event(
        correlation_id: &str,
        idempotency_key: &str,
        processed_at_unix_ms: u64,
    ) -> BoundaryAuditEvent {
        let authenticated = AuthenticatedBoundaryEnvelope::sign(
            boundary_envelope(correlation_id, idempotency_key),
            key_id("unknown-key"),
            &authentication_key(),
        )
        .expect("test envelope must be signed");

        let error = BoundaryError {
            code: BoundaryErrorCode::InvalidRequest,
            message: "boundary envelope references an unknown or unusable key ID".to_owned(),
            retryable: false,
        };

        BoundaryAuditEvent::rejected_from_authenticated(
            &authenticated,
            &error,
            processed_at_unix_ms,
        )
    }

    #[test]
    fn status_view_reports_empty_audit_report() {
        let report = BoundaryAuditReport::new(&[]);
        let status = BoundaryAuditStatusView::from_report(&report);

        assert_eq!(status.verdict(), &BoundaryAuditReportVerdict::Empty);
        assert_eq!(status.verdict_label(), "empty");
        assert_eq!(status.total_count(), 0);
        assert_eq!(status.accepted_count(), 0);
        assert_eq!(status.rejected_count(), 0);
        assert_eq!(status.latest_processed_at_unix_ms(), None);
        assert!(status.is_empty());
        assert!(!status.has_rejections());
    }

    #[test]
    fn status_view_reports_accepted_only_audit_report() {
        let events = vec![
            accepted_event("corr-status-ok-1", "idem-status-ok-1", 2_000),
            accepted_event("corr-status-ok-2", "idem-status-ok-2", 3_000),
        ];

        let report = BoundaryAuditReport::new(&events);
        let status = BoundaryAuditStatusView::from_report(&report);

        assert_eq!(status.verdict(), &BoundaryAuditReportVerdict::AcceptedOnly);
        assert_eq!(status.verdict_label(), "accepted_only");
        assert_eq!(status.total_count(), 2);
        assert_eq!(status.accepted_count(), 2);
        assert_eq!(status.rejected_count(), 0);
        assert_eq!(status.latest_processed_at_unix_ms(), Some(3_000));
        assert!(!status.is_empty());
        assert!(!status.has_rejections());
    }

    #[test]
    fn status_view_reports_audit_report_with_rejections() {
        let events = vec![
            accepted_event("corr-status-ok", "idem-status-ok", 2_000),
            rejected_event("corr-status-fail", "idem-status-fail", 2_500),
        ];

        let report = BoundaryAuditReport::new(&events);
        let status = BoundaryAuditStatusView::from_report(&report);

        assert_eq!(
            status.verdict(),
            &BoundaryAuditReportVerdict::ContainsRejections
        );
        assert_eq!(status.verdict_label(), "contains_rejections");
        assert_eq!(status.total_count(), 2);
        assert_eq!(status.accepted_count(), 1);
        assert_eq!(status.rejected_count(), 1);
        assert_eq!(status.latest_processed_at_unix_ms(), Some(2_500));
        assert!(!status.is_empty());
        assert!(status.has_rejections());
    }
}
