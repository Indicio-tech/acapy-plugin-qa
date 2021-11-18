from marshmallow import fields
from typing import Dict, List, Optional
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.valid import UUIDFour
from ..message_types import PROTOCOL_PACKAGE, ANSWER

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.answer_handler.AnswerHandler"

class Answer(AgentMessage):
    """Class representing the answer message"""

    class Meta:
        """Answer Meta"""
        handler_class = HANDLER_CLASS
        message_type = ANSWER
        schema_class = "AnswerSchema"

    def __init__(
        self,
        *,
        thread_id: str,
        question_text: str,
        question_detail: Optional[str] = None,
        response_index: int,
        **kwargs,
    ):

        """Initialize answer message."""
        super().__init__(**kwargs)

        self.thread_id = thread_id
        self.question_text = question_text
        self.question_detail = question_detail
        self.response_index = response_index


class AnswerSchema(AgentMessageSchema):
    """Schema for Answer message."""

    class Meta:
        model_class = ANSWER

    thread_id = fields.Str(
        required=True,
        description=(
            "Thread ID used for connecting answer to question."
        ),
        example=UUIDFour.EXAMPLE,
    )
    question_text = fields.Str(
        required=True,
        description=(
            "The text of the question."
        )
    )
    question_detail = fields.Str(
        required=False,
        description=(
            "This is optional fine-print giving context to the question and its various answers."
        )
    )
    response_index = fields.Int(
        required=True,
        description=(
            "The index of the chosen response from the list of valid responses."
        )
    )