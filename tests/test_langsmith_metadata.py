from langgraph_course.email_workflow.langsmith import (
    build_workflow_metadata,
    build_workflow_tags,
    summarize_workflow_outputs,
)


def test_build_workflow_metadata_includes_filterable_fields() -> None:
    state = {
        "email_id": "email-123",
        "sender_email": "customer@example.com",
        "classification": {
            "intent": "billing",
            "urgency": "high",
            "topic": "duplicate charge",
            "summary": "Customer charged twice.",
        },
        "ticket_id": "",
        "__interrupt__": [{"value": "review"}],
    }

    metadata = build_workflow_metadata(
        state=state,
        thread_id="thread-123",
        source="manual",
        phase="start",
    )

    assert metadata["workflow_name"] == "email-agent"
    assert metadata["workflow_source"] == "manual"
    assert metadata["workflow_phase"] == "start"
    assert metadata["thread_id"] == "thread-123"
    assert metadata["intent"] == "billing"
    assert metadata["urgency"] == "high"
    assert metadata["human_review_required"] is True
    assert metadata["bug_ticket_created"] is False
    assert metadata["interrupted"] is True


def test_build_workflow_tags_include_review_and_ticket_dimensions() -> None:
    state = {
        "classification": {
            "intent": "bug",
            "urgency": "critical",
            "topic": "unsafe product",
            "summary": "Critical bug.",
        },
        "ticket_id": "BUG-0001",
        "sent_status": "sent",
    }

    tags = build_workflow_tags(
        state=state,
        source="eval",
        phase="resume_review",
        review_outcome="edited",
    )

    assert "workflow:email-agent" in tags
    assert "source:eval" in tags
    assert "phase:resume_review" in tags
    assert "intent:bug" in tags
    assert "urgency:critical" in tags
    assert "review-required:true" in tags
    assert "bug-ticket:true" in tags
    assert "review-outcome:edited" in tags
    assert "sent-status:sent" in tags


def test_summarize_workflow_outputs_keeps_root_trace_compact() -> None:
    state = {
        "email_id": "email-123",
        "classification": {
            "intent": "question",
            "urgency": "low",
            "topic": "sale timing",
            "summary": "Simple question.",
        },
        "sent_status": "sent",
    }

    summary = summarize_workflow_outputs(state)

    assert summary == {
        "email_id": "email-123",
        "intent": "question",
        "urgency": "low",
        "ticket_id": None,
        "sent_status": "sent",
        "interrupted": False,
    }
