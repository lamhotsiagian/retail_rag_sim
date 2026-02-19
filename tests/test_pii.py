from retail_rag_sim.tools.pii import redact_pii

def test_redact_email():
    assert "[REDACTED_EMAIL]" in redact_pii("Email test@example.com")

def test_redact_phone():
    assert "[REDACTED_PHONE]" in redact_pii("Call 312-555-1212")
