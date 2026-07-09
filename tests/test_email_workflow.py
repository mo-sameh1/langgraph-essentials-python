from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from langgraph_course.email_workflow import (
    EmailWorkflowServices,
    EmailWorkflowSession,
    KnowledgeBase,
    KnowledgeDocument,
    build_email_workflow,
)


class StubStructuredRunnable:
    def __init__(self, payload: dict[str, Any], schema: type) -> None:
        self.payload = payload
        self.schema = schema

    def invoke(self, input: str) -> Any:
        del input
        return self.schema(**self.payload)


class StubChatModel:
    def __init__(self, *, classification: dict[str, Any], draft_response: str) -> None:
        self.classification = classification
        self.draft_response = draft_response

    def with_structured_output(
        self,
        schema: type,
        *,
        method: str = "json_schema",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> StubStructuredRunnable:
        del method, include_raw, kwargs
        return StubStructuredRunnable(self.classification, schema)

    def invoke(self, input: str) -> AIMessage:
        del input
        return AIMessage(content=self.draft_response)


def make_services(*, classification: dict[str, Any], draft_response: str) -> EmailWorkflowServices:
    return EmailWorkflowServices(
        llm=StubChatModel(classification=classification, draft_response=draft_response),
        knowledge_base=KnowledgeBase(
            documents=[
                KnowledgeDocument(
                    title="Fallback policy",
                    content="Use the available customer support context.",
                    tags=("general",),
                )
            ]
        ),
    )


def test_low_priority_question_sends_without_review() -> None:
    services = make_services(
        classification={
            "intent": "question",
            "urgency": "low",
            "topic": "sale_duration",
            "summary": "Customer asks how long the sale lasts.",
        },
        draft_response="The sale is currently scheduled through the weekend.",
    )
    graph = build_email_workflow(services, checkpointer=InMemorySaver())
    session = EmailWorkflowSession(graph, thread_id="question-thread")

    result = session.start(
        email_content="Can you tell me how long the sale is on?",
        sender_email="customer@example.com",
        email_id="email-question",
    )

    assert "__interrupt__" not in result
    assert result.get("sent_status") == "sent"
    assert result.get("sent_reply") == "The sale is currently scheduled through the weekend."
    assert result.get("classification", {}).get("intent") == "question"
    assert len(services.sent_replies) == 1


def test_bug_report_interrupts_then_resumes() -> None:
    services = make_services(
        classification={
            "intent": "bug",
            "urgency": "critical",
            "topic": "wheel_failure",
            "summary": "Customer says the tire will not stay attached to the car.",
        },
        draft_response="We are escalating this immediately and opened a defect ticket for you.",
    )
    graph = build_email_workflow(services, checkpointer=InMemorySaver())
    session = EmailWorkflowSession(graph, thread_id="bug-thread")

    first_result = session.start(
        email_content="The tire won't stay on the car!",
        sender_email="customer@example.com",
        email_id="email-bug",
    )

    assert "__interrupt__" in first_result
    assert first_result.get("ticket_id", "").startswith("BUG-")
    assert first_result.get("classification", {}).get("intent") == "bug"
    assert "draft_response" in first_result

    final_result = session.resume_review(
        approved=True,
        edited_response="We opened a priority defect ticket and escalated your case.",
    )

    assert final_result.get("sent_status") == "sent"
    assert (
        final_result.get("sent_reply")
        == "We opened a priority defect ticket and escalated your case."
    )
    assert len(services.sent_replies) == 1
    assert services.sent_replies[0].email_id == "email-bug"


def test_human_rejection_ends_without_sending() -> None:
    services = make_services(
        classification={
            "intent": "billing",
            "urgency": "high",
            "topic": "duplicate_charge",
            "summary": "Customer says they were charged twice.",
        },
        draft_response="We are reviewing the duplicate charge and will follow up shortly.",
    )
    graph = build_email_workflow(services, checkpointer=InMemorySaver())
    session = EmailWorkflowSession(graph, thread_id="billing-thread")

    first_result = session.start(
        email_content="I was charged twice for my subscription.",
        sender_email="customer@example.com",
        email_id="email-billing",
    )

    assert "__interrupt__" in first_result

    final_result = session.resume_review(approved=False)

    assert final_result.get("sent_status") == "cancelled"
    assert services.sent_replies == []
